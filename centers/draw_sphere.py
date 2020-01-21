# already tested pdbs: 1GXD
# pdbs to test: 1OPH 2O8V 

from pymol.cgo import *
from pymol import cmd
import numpy as np
import random
import json

DIAM = 80.0 # diameter of the spheres

def showSphere(centers):
    spherelist = []
    i = 0
    n = centers.shape[0]
    while i < n:
        spherelist.extend([COLOR, random.random(), random.random(), random.random(),
                            SPHERE, centers[i, 0], centers[i, 1], centers[i, 2], DIAM / 2])
        i += 1
    print("Spherelist is {}".format(spherelist))
    cmd.load_cgo(spherelist, 'spheres',   1)


with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/centers_1oph.json') as json_file:
    data = json.load(json_file)
showSphere(np.asarray(data))

