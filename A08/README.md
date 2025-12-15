# A08: ChEMBL lookup by SMILES (Flask)

This app provides a simple web interface where the user enters a chemical structure in SMILES format. After submitting the form, the server queries the ChEMBL web services using the official Python client `chembl_webresource_client` and displays information about the first compound returned from the search.

## Folder location

All files for this assignment are located in the repository subfolder:

`A08/`

## Functionality

- Web page with a form to enter SMILES
- On submit, the server performs a ChEMBL similarity search (threshold configurable)
- The app takes the first hit, fetches full molecule details, and displays key properties:
  - ChEMBL ID, preferred name, molecule type
  - molecular formula, molecular weight (freebase), AlogP, HBD/HBA, PSA, RO5 violations
  - canonical SMILES, InChI, InChIKey
  - synonyms (first 20)

## Clone the repository

```bash
git clone https://github.com/jhrusakUK/ci2.git
cd ci2/A08

# Create virtual environment
python3 -m venv venv

## Activate virtual environment
##- Linux / macOS:
source venv/bin/activate
## Windows (PowerShell):
.\venv\Scripts\Activate.ps1

## Install system requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

## Run the app
python app.py
Use ctrl+click on the link which will appear in the cmd dialogue to open the web application
The web application dialogue will ask for a SMILES string of the desired compound and a similarity threshold
After entering the data, the app will fetch and return chemical data from the web

##How to use the web application

	1. Enter a SMILES string into the form 

	2. Optionally set the similarity threshold (70-100); default is 95

	3. Click Search

	4. The result page shows a table with the extracted information for the first hit

	5. Enter a new SMILES in the same form to perform another search

	If the SMILES is empty or the query returns no hits, the page shows an error message and keeps the form available.

##Example

- Enter SMILES: O=C(O)c1ccccc1
- Example of the compound-related text content that appears on the results page (fields shown by the app):

	Preferred name: BENZOIC ACID

	ChEMBL ID: CHEMBL541

	Molecule type: Small molecule

	Molecular formula: C7H6O2

	Canonical SMILES: O=C(O)c1ccccc1

	Synonyms (examples): Acidum benzoicum; Benzoate; BENZOIC ACID (E 210)


	