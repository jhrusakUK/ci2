\# Clone the repository

git clone https://github.com/jhrusakUK/ci2.git

cd ci2



\# Go to assignment A04

cd A04



\# Create virtual environment

python3 -m venv venv



\# Activate virtual environment

\# Linux / macOS:

source venv/bin/activate

\# Windows (PowerShell):

&nbsp;.\\venv\\Scripts\\Activate.ps1



\# Run the script 



python db.py country.csv countrylanguage.csv city.csv



\# later (when the SQLite file is already created), the script can be run just by



python db.py

