A09



This application extends the previous assignment by implementing a single-page chemistry web server.  

The user enters a chemical structure in SMILES format, the backend retrieves compound data from ChEMBL, generates a 3D molecular image using command-line tools (`obabel` and `povray`), and returns all results to the browser via a JSON API.  

The page content is updated dynamically using JavaScript, without opening any additional pages.



**If you are on Windows and do not have WSL installed:**



1\. Open PowerShell as Administrator

2\. Run

&nbsp;  wsl --install

3\. Restart computer when prompted

4\. Launch ubuntu in powershell. Run:

&nbsp;	wsl



&nbsp;  and create a Linux username and password.

5\. Verify that wsl is running:

&nbsp;	uname -a 



**Install system dependencies**



1\. Run the following commands inside Ubuntu (WSL) terminal:

&nbsp;	sudo apt update

&nbsp;	sudo apt install -y python3 python3-pip python3-venv openbabel povray



2\. Verify installation:

&nbsp;	obabel -V

&nbsp;	povray -version



**Clone the repository**



Inside WSL, navigate to where you want the project and clone it:



&nbsp;	git clone https://github.com/jhrusakUK/ci2.git

&nbsp;	cd ci2/A09



**Create and activate a Python virtual environment:**



&nbsp;	python3 -m venv .venv

&nbsp;	source .venv/bin/activate



**Upgrade pip and install Python dependencies:**



&nbsp;	python -m pip install --upgrade pip

&nbsp;	pip install -r requirements.txt



**Run the server**



&nbsp;	python app.py



as part of the printed message, there will be an URL link to the web application. Use Ctrl + \[left\_click] to open it.



Stop the server using Ctrl + C.



**How to use the web application**



1. Open the web page in your browser



2\. Enter a SMILES string (example: O=C(O)c1ccccc1)



3\. Click Search



4\. The page updates dynamically and displays:



&nbsp;	compound data retrieved from ChEMBL



&nbsp;	a generated 3D PNG image of the molecule



If the SMILES is invalid or no compound is found, an error message is displayed on the same page.



**Notes on rendering and dependencies**



Generated images are stored in:



&nbsp;	A09/static/renders/





The application explicitly configures POV-Ray to locate Open Babel include files

(e.g. babel\_povray3.inc) to ensure compatibility on Debian/Ubuntu systems.



If obabel or povray are missing, the backend returns a clear error message.





