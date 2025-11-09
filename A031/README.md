## How to run A03

```bash
# Clone the repository
git clone https://github.com/jhrusakUK/ci2.git
cd ci2

# Go to assignment A03
cd A031

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux / macOS:
source venv/bin/activate
# Windows (PowerShell):
# .\venv\Scripts\Activate.ps1

# Install BeautifulSoup
pip install beautifulsoup4>=4.12

# Run the script (HTML file downloaded from Molbase search for "benzidine")

python molbase_parser.py molbase_benzidine.html

