from Bio.PDB import *
import glob
import json

DIAM = 90.0 # diameter of the spheres
path = "/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/1gxd_2/"

with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/centers.json') as json_file:
    data = json.load(json_file)
center = data[1]
print("Center: {}".format(center))

ligs = glob.glob(path + "*.pdb")
ligs_in = []
parser = PDBParser()

for lig in ligs:
    structure = parser.get_structure('mymol', lig)
    for atom in structure.get_atoms():
        x, y, z = atom.get_coord()
        if (x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2 < (DIAM / 2)**2:
            ligs_in.append(lig)
            break
print("{} out of {} is inside the sphere".format(len(ligs_in), len(ligs)))
with open('ligs_in.json', 'w') as outfile:
    json.dump(ligs_in, outfile)