import glob
import os
from rdkit import Chem
from rdkit.Chem import Draw

def main():
    # Find all .mol files in current folder
    mol_files = sorted(glob.glob("*.mol"))
    if not mol_files:
        print("No MOL files found in the folder.")
        return

    rows = []

    for mol_file in mol_files:
        try:
            # Bypass valence errors
            mol = Chem.MolFromMolFile(mol_file, sanitize=False)
            if mol is None:
                print(f"Failed to read {mol_file}")
                continue

            # Optionally sanitize atoms ignoring valence
            try:
                Chem.SanitizeMol(mol, sanitizeOps=Chem.SanitizeFlags.SANITIZE_ALL ^ Chem.SanitizeFlags.SANITIZE_PROPERTIES)
            except:
                # Ignore valence errors
                pass

            png_file = mol_file.replace(".mol", ".png")
            Draw.MolToFile(mol, png_file, size=(300,300))
            rows.append((mol_file, png_file))
        except Exception as e:
            print(f"Error processing {mol_file}: {e}")

    if not rows:
        print("No PNG images created. Exiting.")
        return

    # Generate HTML file
    html_file = "index.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n")
        f.write("<title>Molecule Structures</title>\n</head>\n<body>\n")
        f.write("<h1>Molecule Structures</h1>\n")
        f.write("<table border='1' cellpadding='5'>\n")
        f.write("<tr><th>filename</th><th>2D structure</th></tr>\n")

        for mol_file, png_file in rows:
            cdxml_name = os.path.splitext(mol_file)[0] + ".cdxml"
            f.write("<tr>")
            f.write(f"<td>{cdxml_name}</td>")
            f.write(f"<td><img src='{png_file}' width='200'></td>")
            f.write("</tr>\n")

        f.write("</table>\n</body>\n</html>")

    print(f"{html_file} generated successfully with {len(rows)} molecules.")

if __name__ == "__main__":
    main()