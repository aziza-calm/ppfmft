# import sblu.rmsd
import numpy as np
import prody
import json

model = '/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/1oph_l.pdb'

with open('ligs_sorted_1oph.json') as json_file:
    ligs = json.load(json_file)

def rmsd(x, y):
    delta = x - y
    N = len(delta)
    np.multiply(delta, delta, delta)
    return np.sqrt((delta.sum() / N))

crys = prody.proteins.parsePDB(model)
for i in range(len(ligs)):
    lig = prody.proteins.parsePDB(ligs[i]['path'])
    crys_coords = crys.getCoords()
    lig_coords = lig.getCoords()
    ligs[i]['rmsd'] = rmsd(crys_coords, lig_coords)

for i in range(len(ligs)):
    print(ligs[i])

with open("sorted_with_rmsd_1oph.json", "w") as output_file:
    json.dump(ligs, output_file)