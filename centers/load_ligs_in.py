from pymol import cmd
import json
import os

with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/ligs_in.json') as json_file:
    ligs_in = json.load(json_file)

for lig in ligs_in:
    cmd.load(lig, os.path.basename(lig))