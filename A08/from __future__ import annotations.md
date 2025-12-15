**from \_\_future\_\_ import annotations**



**from typing import Any, Dict, List, Optional, Tuple**



**from flask import Flask, render\_template, request**

**from chembl\_webresource\_client.new\_client import new\_client**





**app = Flask(\_\_name\_\_)**





**def \_first\_similarity\_hit(smiles: str, threshold: int) -> Optional\[Dict\[str, Any]]:**

    **"""**

    **Return the first similarity hit dict from ChEMBL for a SMILES query.**

    **Uses the 'similarity' resource from chembl\_webresource\_client.**

    **"""**

    **sim = new\_client.similarity**



    **# similarity endpoint expects integer threshold in \[70..100] (practically).**

    **# Keep it robust and clamp.**

    **if threshold < 70:**

        **threshold = 70**

    **if threshold > 100:**

        **threshold = 100**



    **# Query similarity search. We take only a small slice for speed.**

    **# The result items usually contain at least molecule\_chembl\_id plus score fields.**

    **results = sim.filter(smiles=smiles, similarity=threshold)\[:10]**

    **if not results:**

        **return None**

    **return results\[0]**





**def \_molecule\_details(chembl\_id: str) -> Optional\[Dict\[str, Any]]:**

    **"""**

    **Fetch full molecule record for a ChEMBL ID.**

    **"""**

    **mol = new\_client.molecule**

    **try:**

        **return mol.get(chembl\_id)**

    **except Exception:**

        **return None**





**def \_safe\_get(d: Dict\[str, Any], path: List\[str], default: Any = None) -> Any:**

    **"""**

    **Nested dict getter: \_safe\_get(m, \["molecule\_properties", "full\_mwt"])**

    **"""**

    **cur: Any = d**

    **for key in path:**

        **if not isinstance(cur, dict) or key not in cur:**

            **return default**

        **cur = cur\[key]**

    **return cur**





**def \_extract\_display\_fields(m: Dict\[str, Any]) -> Dict\[str, Any]:**

    **"""**

    **Convert raw ChEMBL molecule dict into a flat dict suitable for display.**

    **"""**

    **props = m.get("molecule\_properties") or {}**

    **structures = m.get("molecule\_structures") or {}**



    **# Synonyms can be large. We keep a concise list.**

    **syns = m.get("molecule\_synonyms") or \[]**

    **synonyms = \[]**

    **for s in syns:**

        **if isinstance(s, dict) and s.get("molecule\_synonym"):**

            **synonyms.append(s\["molecule\_synonym"])**

    **# De-duplicate while preserving order**

    **seen = set()**

    **synonyms\_unique = \[]**

    **for s in synonyms:**

        **if s not in seen:**

            **seen.add(s)**

            **synonyms\_unique.append(s)**



    **return {**

        **"ChEMBL ID": m.get("molecule\_chembl\_id"),**

        **"Preferred name": m.get("pref\_name") or "(not available)",**

        **"Molecule type": m.get("molecule\_type") or "(not available)",**

        **"Max phase": m.get("max\_phase"),**

        **"Molecular formula": props.get("full\_molformula"),**

        **"Molecular weight (freebase)": props.get("mw\_freebase"),**

        **"AlogP": props.get("alogp"),**

        **"HBD": props.get("hbd"),**

        **"HBA": props.get("hba"),**

        **"PSA": props.get("psa"),**

        **"RO5 violations": props.get("ro5\_violations"),**

        **"Canonical SMILES": structures.get("canonical\_smiles"),**

        **"Standard InChI": structures.get("standard\_inchi"),**

        **"Standard InChIKey": structures.get("standard\_inchi\_key"),**

        **"Synonyms (first 20)": synonyms\_unique\[:20],**

    **}**





**@app.route("/", methods=\["GET", "POST"])**

**def index():**

    **smiles = ""**

    **threshold = 95  # default similarity threshold**

    **error = None**

    **hit = None**

    **fields = None**



    **if request.method == "POST":**

        **smiles = (request.form.get("smiles") or "").strip()**

        **threshold\_raw = (request.form.get("threshold") or "").strip()**



        **if threshold\_raw:**

            **try:**

                **threshold = int(threshold\_raw)**

            **except ValueError:**

                **threshold = 95**



        **if not smiles:**

            **error = "Please enter a SMILES string."**

        **else:**

            **try:**

                **first\_hit = \_first\_similarity\_hit(smiles, threshold)**

                **if not first\_hit:**

                    **error = "No compounds found in ChEMBL for this query."**

                **else:**

                    **chembl\_id = first\_hit.get("molecule\_chembl\_id")**

                    **if not chembl\_id:**

                        **error = "A result was returned, but it did not include a ChEMBL ID."**

                    **else:**

                        **hit = first\_hit**

                        **mol = \_molecule\_details(chembl\_id)**

                        **if not mol:**

                            **error = f"Could not retrieve details for {chembl\_id}."**

                        **else:**

                            **fields = \_extract\_display\_fields(mol)**

            **except Exception as e:**

                **error = f"Request failed: {e}"**



    **return render\_template(**

        **"index.html",**

        **smiles=smiles,**

        **threshold=threshold,**

        **error=error,**

        **hit=hit,**

        **fields=fields,**

    **)**





**if \_\_name\_\_ == "\_\_main\_\_":**

    **# Debug can be turned off for submission, but is convenient locally.**

    **app.run(host="127.0.0.1", port=5000, debug=True)**



