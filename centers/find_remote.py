from Bio.PDB import *
import json

DIAM = 20.0 # diameter of the spheres

def findMostRemote():
    parser = PDBParser()
    structure = parser.get_structure('mymol', '/home/aziza/1gxd.pdb')
    max_dist = -5.0
    for model in structure:
        for chain in model:
            for residue1 in chain:
                for model in structure:
                    for chain in model:
                        for residue2 in chain:
                            try:
                                if max_dist < residue1['CA'] - residue2['CA']:
                                    max_dist = residue1['CA'] - residue2['CA']
                                    dot1 = residue1['CA'].get_coord()
                                    dot2 = residue2['CA'].get_coord()
                            except KeyError:
                                continue
    # for atom1 in structure.get_atoms():
    #     for atom2 in structure.get_atoms():
    #         if max_dist < atom1 - atom2:
    #             max_dist = atom1 - atom2
    #             dot1 = atom1.get_coord()
    #             dot2 = atom2.get_coord()
    print(max_dist)
    print(type(dot1), dot1)
    print(type(dot2), dot2)
    return dot1, dot2

def findTraegheitsellipsoid():
    pass

def findCenters(dot1, dot2, n_centr, ):
    parser = PDBParser()
    structure = parser.get_structure('mymol', '/home/aziza/1gxd.pdb')
    for atom in structure.get_atoms():
        pass


if __name__=='__main__':
    dot1, dot2 = findMostRemote()
    data = {}
    data['dot1'] = dot1.tolist()
    data['dot2'] = dot2.tolist()
    with open('remote_dots.json', 'w') as outfile:
        json.dump(data, outfile)