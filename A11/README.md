It is a Django project with one application and three pages:



\- \*\*A) Home\*\*: welcome page and links to all pages  

\- \*\*B) ChEMBL\*\*: user enters SMILES; the server queries ChEMBL and displays information about the first matching compound. Each submitted SMILES is stored in the database together with the submission time.  

\- \*\*C) Povray\*\*: user enters SMILES; the server generates a 3D PNG image using Open Babel and POV-Ray, saves it to a Django static folder, and displays it on the page.  



All pages use Django templates:

\- Home page provides the base layout, header, and navigation menu.

\- ChEMBL and Povray pages extend the base template and override only the main content block.



---



\## System requirements (Linux / WSL recommended)



This assignment requires command-line tools for rendering:



\- Open Babel (`obabel`)

\- POV-Ray (`povray`)



**If you are on Windows and do not have WSL installed:**



1\. Open PowerShell as Administrator



2\. Run



  wsl --install



3\. Restart computer when prompted



4\. Launch ubuntu in powershell. Run:



  wsl



  and create a Linux username and password.



5\. Verify that wsl is running:



  uname -a





On Ubuntu / WSL:



```bash

sudo apt update

sudo apt install -y python3 python3-pip python3-venv openbabel povray



**Clone git repository**



Inside WSL, navigate to where you want the project and clone it:



&nbsp; git clone https://github.com/jhrusakUK/ci2.git



&nbsp; cd ci2/A10



**Create and activate a Python virtual environment:**



&nbsp; python3 -m venv .venv



&nbsp; source .venv/bin/activate



**Upgrade pip and install Python dependencies:**



&nbsp; python -m pip install --upgrade pip



&nbsp; pip install -r requirements.txt



**Initialize the database:**



&nbsp; python manage.py makemigrations



&nbsp; python manage.py migrate



&nbsp; ## This creates an SQLite database file db.sqlite3 and creates the table used to store SMILES submissions.



**Run the Django development server:**



&nbsp; python manage.py runserver

  

  ## run the server by CTRL + left click on the IP address shown by CMD. Exit the server by CTRL + C





















