from __future__ import annotations

import os
import re
import uuid
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import quote

import requests
from flask import Flask, jsonify, render_template, request, url_for


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
RENDERS_DIR = STATIC_DIR / "renders"
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"

app = Flask(__name__)


# Very lightweight input sanity check (not a full SMILES validator).
# Blocks clearly dangerous inputs (newlines, extremely long strings, etc.).
_SMILES_ALLOWED = re.compile(r"^[A-Za-z0-9@\+\-\[\]\(\)=#\\/\.:%\*]+$")


def _smiles_ok(smiles: str) -> bool:
    if not smiles:
        return False
    if len(smiles) > 300:
        return False
    if "\n" in smiles or "\r" in smiles or "\t" in smiles:
        return False
    return bool(_SMILES_ALLOWED.match(smiles))


def chembl_find_first_by_smiles(smiles: str) -> Optional[Dict[str, Any]]:
    """
    Find the first ChEMBL molecule matching SMILES using flexmatch:
    /molecule?molecule_structures__canonical_smiles__flexmatch=<SMILES>&limit=1
    """
    smiles_enc = quote(smiles, safe="")
    url = (
        f"{CHEMBL_BASE}/molecule.json?"
        f"molecule_structures__canonical_smiles__flexmatch={smiles_enc}"
        f"&limit=1"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    molecules = data.get("molecules") or []
    if not molecules:
        return None
    return molecules[0]


def chembl_get_molecule_details(chembl_id: str) -> Dict[str, Any]:
    url = f"{CHEMBL_BASE}/molecule/{chembl_id}.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def extract_display_fields(m: Dict[str, Any]) -> Dict[str, Any]:
    props = m.get("molecule_properties") or {}
    structures = m.get("molecule_structures") or {}

    syns = m.get("molecule_synonyms") or []
    synonyms = []
    for s in syns:
        if isinstance(s, dict) and s.get("molecule_synonym"):
            synonyms.append(s["molecule_synonym"])

    seen = set()
    syn_unique = []
    for s in synonyms:
        if s not in seen:
            seen.add(s)
            syn_unique.append(s)

    return {
        "ChEMBL ID": m.get("molecule_chembl_id"),
        "Preferred name": m.get("pref_name") or "(not available)",
        "Molecule type": m.get("molecule_type") or "(not available)",
        "Max phase": m.get("max_phase"),
        "Molecular formula": props.get("full_molformula"),
        "Molecular weight (freebase)": props.get("mw_freebase"),
        "AlogP": props.get("alogp"),
        "HBD": props.get("hbd"),
        "HBA": props.get("hba"),
        "PSA": props.get("psa"),
        "RO5 violations": props.get("ro5_violations"),
        "Canonical SMILES": structures.get("canonical_smiles"),
        "Standard InChI": structures.get("standard_inchi"),
        "Standard InChIKey": structures.get("standard_inchi_key"),
        "Synonyms (first 20)": syn_unique[:20],
    }


def _run(cmd: list[str], timeout: int = 60) -> None:
    """
    Run a command and raise a readable error if it fails.
    """
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command failed:\n{' '.join(cmd)}\n\nSTDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}"
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Command timed out:\n{' '.join(cmd)}") from e


def render_3d_png_from_smiles(smiles: str) -> str:
    """
    Create a 3D image from SMILES using Open Babel + POV-Ray.
    Saves a PNG into static/renders and returns the relative URL path.
    """
    # Unique name per request to avoid collisions
    token = uuid.uuid4().hex
    pdb_path = RENDERS_DIR / f"{token}.pdb"
    pov_path = RENDERS_DIR / f"{token}.pov"
    png_path = RENDERS_DIR / f"{token}.png"

    # 1) Generate 3D coordinates into PDB
    # obabel -:"SMILES" -O out.pdb --gen3d
    _run(["obabel", f"-:{smiles}", "-O", str(pdb_path), "--gen3d"], timeout=60)

    # 2) Convert to POV-Ray scene file
    # obabel out.pdb -O out.pov
    _run(["obabel", str(pdb_path), "-O", str(pov_path)], timeout=60)

    # 3) Render PNG via povray
    # +W +H set resolution, +FN for PNG output, +D display off, +V verbose off
    _run(
    [
        "povray",
        f"+I{pov_path}",
        f"+O{png_path}",
        "+L/usr/share/povray/include",
        "+W800",
        "+H600",
        "+FN",
        "+D",
        "+V",
    ],
    timeout=90,
)

    # Optional cleanup: keep PNG and remove intermediate files
    try:
        if pdb_path.exists():
            pdb_path.unlink()
        if pov_path.exists():
            pov_path.unlink()
    except Exception:
        # Not critical
        pass

    # Return URL usable by browser (cache-bust with ?v=token if desired)
    return url_for("static", filename=f"renders/{token}.png")


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/lookup")
def api_lookup():
    data = request.get_json(silent=True) or {}
    smiles = (data.get("smiles") or "").strip()

    if not _smiles_ok(smiles):
        return jsonify({"ok": False, "error": "Invalid SMILES (empty or contains unsupported characters)."}), 400

    try:
        first = chembl_find_first_by_smiles(smiles)
        if not first or not first.get("molecule_chembl_id"):
            return jsonify({"ok": False, "error": "No compound found in ChEMBL for this SMILES."}), 404

        chembl_id = first["molecule_chembl_id"]
        details = chembl_get_molecule_details(chembl_id)
        fields = extract_display_fields(details)

        image_url = render_3d_png_from_smiles(smiles)

        return jsonify(
            {
                "ok": True,
                "query_smiles": smiles,
                "chembl_id": chembl_id,
                "fields": fields,
                "image_url": image_url,
            }
        )
    except requests.RequestException as e:
        return jsonify({"ok": False, "error": f"ChEMBL request failed: {e}"}), 502
    except FileNotFoundError as e:
        # obabel or povray not installed / not on PATH
        return jsonify(
            {
                "ok": False,
                "error": "Missing system dependency. Make sure 'obabel' and 'povray' are installed and available in PATH.",
            }
        ), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    # Debug True for development; set False for final if desired.
    app.run(host="127.0.0.1", port=5000, debug=True)