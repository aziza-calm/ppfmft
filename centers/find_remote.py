from Bio.PDB import *
import json
import numpy as np
import time

DIAM = 25.0 # diameter of the spheres
molec = '/home/aziza/1oph.pdb'

def findMostRemote():
    parser = PDBParser()
    structure = parser.get_structure('mymol', molec)
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
    return dot1, dot2


def findTraegheitsellipsoid():
    pass


def darin(coord, a1, r, dist):
    """
    darin() function defines if the atom with coordinates coord
    belongs to the area between a(i) and a(i + 1) surfaces
    ("darin" from german "inside")
    It takes 4 arguments:
        p - coordinates of the atom
        a1 - A(i) dot, where one of the surfaces liegt
        r - vector between two most remote CA atoms (our line, axis)
        dist - module of r vector
    and returns True, if belongs, and False in other cases.
    """
    p = np.asarray(coord)
    # the other surface
    a2 = a1 + r * DIAM / dist
    if np.dot(p - a1, a2 - a1) > 0 and np.dot(p - a2, a1 - a2):
        return True
    return False


def findCenters(dot1, dot2):
    start = np.array(dot1)
    end = np.array(dot2)
    dist = np.linalg.norm(start - end)
    print("Distance is {}".format(dist))
    r = end - start
    numb_centers = dist / DIAM / 0.9
    anfangs = np.zeros((int(numb_centers), 3), dtype=np.float64)
    delta = r * DIAM * 0.9 / dist
    anfangs[0, :] = start - r * 0.1 * DIAM / dist
    i = 1
    print(anfangs.shape)
    while i < int(numb_centers):
        anfangs[i, :] = anfangs[i - 1, :] + delta
        i += 1
    print("Anfangs {}".format(anfangs))

    # теперь основная часть, находим центры как среднее всех координат атомов, которые входят в сферу
    
    parser = PDBParser()
    structure = parser.get_structure('mymol', molec)
    centers = np.zeros((int(numb_centers), 4), dtype=np.float64)
    # Для каждой области (это уже не сферы)
    for i in range(int(numb_centers)):
        for atom in structure.get_atoms():
            # проверяем лежит ли атом в этой области
            if darin(atom.get_coord(), anfangs[i], r, dist):
                centers[i, :3] = centers[i, :3] + atom.get_coord()
                centers[i, 3] += 1
    for i in range(int(numb_centers)):
        centers[i, :3] /= centers[i, 3]
    with open('centers.json', 'w') as outfile:
        json.dump(centers[:, :3].tolist(), outfile)
    print(centers)


if __name__=='__main__':
    dot1, dot2 = findMostRemote()
    data = {}
    data['dot1'] = dot1.tolist()
    data['dot2'] = dot2.tolist()
    with open('remote_dots.json', 'w') as outfile:
        json.dump(data, outfile)

    time.sleep(20)

    with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/remote_dots.json') as json_file:
        data = json.load(json_file)
    dot1 = data['dot1']
    dot2 = data['dot2']
    findCenters(dot1, dot2)