\# Clone the repository

git clone https://github.com/jhrusakUK/ci2.git

cd ci2



\# Go to assignment A05

cd A05



\# Create virtual environment

python3 -m venv venv



\# Activate virtual environment

\# Linux / macOS:

source venv/bin/activate

\# Windows (PowerShell):

 .\\venv\\Scripts\\Activate.ps1



\#unzip the .zip file to the A05 folder

\#in cmd, navigate to A05 folder and run the following command

obabel \*.cdx -O\*.mol

\#this will create .mol files, which will be recognized by the python script



\# Run the script

python cdx2html.py





