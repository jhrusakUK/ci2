**If you are on Windows and do not have WSL installed:**



1\. Open PowerShell as Administrator



2\. Run



&nbsp; wsl --install



3\. Restart computer when prompted



4\. Launch ubuntu in powershell. Run:



&nbsp; wsl



&nbsp; and create a Linux username and password.



5\. Verify that wsl is running:



&nbsp; uname -a



**Install system dependencies**



1\. Run the following commands inside Ubuntu (WSL) terminal:



&nbsp; sudo apt update



&nbsp; sudo apt install -y python3 python3-pip python3-venv openbabel povray



2\. Verify installation:



&nbsp; obabel -V



&nbsp; povray -version



**Clone the git repository**



Inside WSL, navigate to where you want the project and clone it:



&nbsp; git clone https://github.com/jhrusakUK/ci2.git



&nbsp; cd ci2/A10



**Create and activate a Python virtual environment:**



&nbsp; python3 -m venv .venv



&nbsp; source .venv/bin/activate



**Upgrade pip and install Python dependencies:**



&nbsp; python -m pip install --upgrade pip



&nbsp; pip install -r requirements.txt



**Install browser dependencies for Playwright (Linux / WSL)**



  sudo apt install -y \\

&nbsp; libnss3 libnspr4 \\

&nbsp; libatk1.0-0 libatk-bridge2.0-0 \\

&nbsp; libcups2 libdrm2 \\

&nbsp; libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \\

&nbsp; libgbm1 libasound2 \\

&nbsp; libpangocairo-1.0-0 libpango-1.0-0 libcairo2 \\

&nbsp; libx11-6 libx11-xcb1 libxcb1 libxext6 libxi6 \\

&nbsp; libglib2.0-0 \\

&nbsp; fonts-liberation



**Install Playwright browser binaries**



  python -m playwright install



&nbsp; python -m playwright --version # verify installation



**Recording browser interaction with Playwright codegen**



 This step requires the server to be running.



&nbsp;Start the server:



&nbsp; python app.py





&nbsp;Open a second terminal, activate the virtual environment, and run:



&nbsp; python -m playwright codegen http://127.0.0.1:5000





&nbsp;In the opened browser:



&nbsp; enter a SMILES string (e.g. O=C(O)c1ccccc1)



&nbsp; click Search



&nbsp; wait for the compound data and image to appear



Playwright will generate Python code describing the interaction.

This code was manually adapted into robust pytest tests in tests/test\_web.py

(using stable selectors and explicit assertions).



**Running the automated tests**



&nbsp;Important:

Do NOT run the server manually when running tests.

The tests start and stop the server automatically.



From the A10 directory with the virtual environment active:



&nbsp; pytest -vv





Expected behavior:



Playwright launches Chromium



Flask server is started automatically on a free port



Tests interact with the page



Rendering with POV-Ray may take several seconds



Tests complete successfully



A short smoke test (test\_smoke.py) is included to verify pytest discovery.



**Notes**



End-to-end tests include real network access (ChEMBL) and 3D rendering

and may take tens of seconds to complete.



Chromium is launched with --no-sandbox and --disable-dev-shm-usage

for compatibility with WSL.



Generated images are stored in:



&nbsp; static/renders/

