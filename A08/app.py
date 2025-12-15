from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import quote

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"


def chembl_find_first_by_smiles(smiles: str) -> Optional[Dict[str, Any]]:
    """
    Find the first ChEMBL molecule matching a SMILES using flexmatch:
    /molecule?molecule_structures__canonical_smiles__flexmatch=<SMILES>

    Returns the first molecule object from the 'molecules' list (if any).
    """
    # URL-encode SMILES because it contains characters like '=', '#', '(', ')', etc.
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
    """
    Retrieve full details for a ChEMBL molecule:
    /molecule/<CHEMBL_ID>.json
    """
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

    # de-duplicate synonyms while preserving order
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


@app.route("/", methods=["GET", "POST"])
def index():
    smiles = ""
    error = None
    fields = None

    if request.method == "POST":
        smiles = (request.form.get("smiles") or "").strip()

        if not smiles:
            error = "Please enter a SMILES string."
        else:
            try:
                first = chembl_find_first_by_smiles(smiles)
                if not first:
                    error = "No compounds found in ChEMBL for this SMILES (flexmatch)."
                else:
                    chembl_id = first.get("molecule_chembl_id")
                    if not chembl_id:
                        error = "ChEMBL returned a record without a molecule_chembl_id."
                    else:
                        details = chembl_get_molecule_details(chembl_id)
                        fields = extract_display_fields(details)
            except requests.RequestException as e:
                error = f"ChEMBL request failed: {e}"
            except Exception as e:
                error = f"Unexpected error: {e}"

    return render_template("index.html", smiles=smiles, error=error, fields=fields)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
