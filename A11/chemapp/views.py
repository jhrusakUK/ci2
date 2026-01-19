import re
import uuid
import subprocess
from pathlib import Path
from urllib.parse import quote

import requests
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone

from .models import SmilesQuery


CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"

_SMILES_ALLOWED = re.compile(r"^[A-Za-z0-9@\+\-\[\]\(\)=#\\/\.:%\*]+$")


def smiles_ok(smiles: str) -> bool:
    if not smiles:
        return False
    if len(smiles) > 300:
        return False
    if "\n" in smiles or "\r" in smiles or "\t" in smiles or " " in smiles:
        return False
    return bool(_SMILES_ALLOWED.match(smiles))


def home(request):
    return render(request, "chemapp/home.html")


def chembl_first_hit(smiles: str):
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


def chembl_details(chembl_id: str):
    url = f"{CHEMBL_BASE}/molecule/{chembl_id}.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def extract_fields(m: dict) -> list[dict]:
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

    fields = [
        ("ChEMBL ID", m.get("molecule_chembl_id")),
        ("Preferred name", m.get("pref_name") or "(not available)"),
        ("Molecule type", m.get("molecule_type") or "(not available)"),
        ("Max phase", m.get("max_phase")),
        ("Molecular formula", props.get("full_molformula")),
        ("Molecular weight (freebase)", props.get("mw_freebase")),
        ("AlogP", props.get("alogp")),
        ("HBD", props.get("hbd")),
        ("HBA", props.get("hba")),
        ("PSA", props.get("psa")),
        ("RO5 violations", props.get("ro5_violations")),
        ("Canonical SMILES", structures.get("canonical_smiles")),
        ("Standard InChI", structures.get("standard_inchi")),
        ("Standard InChIKey", structures.get("standard_inchi_key")),
        ("Synonyms (first 20)", syn_unique[:20]),
    ]

    rows = []
    for k, v in fields:
        rows.append({"key": k, "value": v, "is_list": isinstance(v, list)})
    return rows


def chembl_lookup(request):
    context = {"fields": None, "error": None, "smiles": "", "history": []}

    history = SmilesQuery.objects.order_by("-created_at")[:10]
    context["history"] = history

    if request.method == "POST":
        smiles = (request.POST.get("smiles") or "").strip()
        context["smiles"] = smiles

        if not smiles_ok(smiles):
            context["error"] = "Invalid SMILES (empty or contains unsupported characters)."
            return render(request, "chemapp/chembl.html", context)

        # Save SMILES + timestamp into DB (requirement)
        SmilesQuery.objects.create(smiles=smiles, created_at=timezone.now())

        try:
            hit = chembl_first_hit(smiles)
            if not hit or not hit.get("molecule_chembl_id"):
                context["error"] = "No compound found in ChEMBL for this SMILES."
                return render(request, "chemapp/chembl.html", context)

            chembl_id = hit["molecule_chembl_id"]
            details = chembl_details(chembl_id)
            context["fields"] = extract_fields(details)

        except requests.RequestException as e:
            context["error"] = f"ChEMBL request failed: {e}"

    return render(request, "chemapp/chembl.html", context)


def run_cmd(cmd: list[str], timeout: int = 90) -> None:
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)


def povray_render(request):
    context = {"image_url": None, "error": None, "smiles": ""}

    if request.method == "POST":
        smiles = (request.POST.get("smiles") or "").strip()
        context["smiles"] = smiles

        if not smiles_ok(smiles):
            context["error"] = "Invalid SMILES (empty or contains unsupported characters)."
            return render(request, "chemapp/povray.html", context)

        # Save renders under app static folder so Django can serve them in dev
        renders_dir = Path(settings.BASE_DIR) / "chemapp" / "static" / "chemapp" / "renders"
        renders_dir.mkdir(parents=True, exist_ok=True)

        token = uuid.uuid4().hex
        pdb_path = renders_dir / f"{token}.pdb"
        pov_path = renders_dir / f"{token}.pov"
        png_path = renders_dir / f"{token}.png"

        try:
            # Generate 3D coords
            run_cmd(["obabel", f"-:{smiles}", "-O", str(pdb_path), "--gen3d"], timeout=60)

            # Convert to POV-Ray scene
            run_cmd(["obabel", str(pdb_path), "-O", str(pov_path)], timeout=60)

            # Render with POV-Ray
            # Add include path so babel_povray3.inc is found
            run_cmd(
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
                timeout=120,
            )

            # cleanup intermediates
            if pdb_path.exists():
                pdb_path.unlink()
            if pov_path.exists():
                pov_path.unlink()

            # URL for static file
            context["image_url"] = f"{settings.STATIC_URL}chemapp/renders/{token}.png"

        except FileNotFoundError:
            context["error"] = "Missing system dependency. Ensure obabel and povray are installed and available in PATH."
        except subprocess.CalledProcessError as e:
            context["error"] = f"Rendering failed. STDERR:\n{e.stderr}"
        except Exception as e:
            context["error"] = f"Unexpected error: {e}"

    return render(request, "chemapp/povray.html", context)
