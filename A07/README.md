# Clone the repository
git clone https://github.com/jhrusakUK/ci2.git
cd ci2

# Go to assignment A07
cd A07

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux / macOS:
source venv/bin/activate
# Windows (PowerShell):
 .\venv\Scripts\Activate.ps1

#Create a file in a text editor containing the SMILES of the molecule, i.e. glycine, save as a .smi file

#from cmd, run the command

obabel gly.smi -O gly.pov

#in POVray interface, generate the file containing 4 glycine molecules at the vertices of a square

// Include Open Babel POV definitions
#include "babel_povray3.inc"

// Include single glycine molecule
#include "gly.pov"

// --------------------------------------------------
// Set output file (Windows POV-Ray uses this)
#declare Output_File_Name = "gly4.png";

// Camera
camera {
    location <0, 15, -25>
    look_at  <0, 0, 0>
}

// Light
light_source {
    <20, 40, -20>
    color rgb <1, 1, 1>
}

// Background
background { color rgb <1,1,1> }

// --------------------------------------------------
// Place 4 glycines at square vertices
// --------------------------------------------------

// Make sure object names match the included glycine molecule name in gly.pov
object { mol_0 translate <0,0,0> }     // bottom-left
object { mol_0 translate <5,0,0> }     // bottom-right
object { mol_0 translate <5,5,0> }     // top-right
object { mol_0 translate <0,5,0> }     // top-left

# click on the "Run" button and this should generate the .png file