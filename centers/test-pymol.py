# already tested pdbs: 1GXD
# pdbs to test: 1OPH 2O8V 

from pymol.cgo import *
from pymol import cmd
import math
import numpy as np
import random
import json

DIAM = 20.0 # diameter of the spheres

def calculateCenters(start, end):
    start = np.array(start)
    end = np.array(end)
    dist = np.linalg.norm(start - end)
    print("Distance is {}".format(dist))
    r = end - start
    numb_centers = dist / DIAM / 0.9
    delta = r / numb_centers / 1.5
    centers = np.zeros((int(numb_centers), 3), dtype=np.float64)
    centers[0, :] = start + delta
    i = 1
    print(centers.shape)
    while i < int(numb_centers):
        centers[i, :] = centers[i - 1, :] + delta * 2
        i += 1
    print("Centers {}".format(centers))
    return centers


def showSphere(centers):
    spherelist = []
    i = 0
    n = centers.shape[0]
    while i < n - 1:
        spherelist.extend([COLOR, random.random(), random.random(), random.random(),
                            SPHERE, centers[i, 0], centers[i, 1], centers[i, 2], DIAM])
        i += 1
    print("Spherelist is {}".format(spherelist))
    cmd.load_cgo(spherelist, 'spheres',   1)


def findSphereCenters(selection="(all)", linewidth=2.0, r=5.0, g=2.0, b=1.0):
    # ([minX, minY, minZ],[maxX, maxY, maxZ]) = cmd.get_extent(selection)

    # size = {'x':maxX - minX, 'y':maxY - minY, 'z':maxZ - minZ}
    # print("x = {}, y = {}, z = {}".format(size['x'], size['y'], size['z']))
    # max_dim = max(size, key=size.get)
    # print("max dimention is {} = {}".format(max_dim, size[max_dim]))

    # line_dot1 = {'x':minX, 'y':minY, 'z':minZ}
    # line_dot2 = {'x':maxX, 'y':maxY, 'z':maxZ}

    # for key in size:
    #     if key != max_dim:
    #         line_dot1[key] = (line_dot1[key] + line_dot2[key]) / 2
    #         line_dot2[key] = line_dot1[key]
    #     else:
    #         line_dot1[key] -= 0.05 * size[max_dim]
    #         line_dot2[key] += 0.05 * size[max_dim]
    
    with open('/home/aziza/Downloads/basa/fmft_suite/fmft_apps/remote_dots.json') as json_file:
        data = json.load(json_file)
    dot1 = data['dot1']
    dot2 = data['dot2']

    line = [
        LINEWIDTH, float(linewidth),

        BEGIN, LINES,
        COLOR, float(r), float(g), float(b),

        VERTEX, dot1[0], dot1[1], dot1[2],
        VERTEX, dot2[0], dot2[1], dot2[2],
    ]
    print("line : {}".format(line))
    line_name = "line"
    cmd.load_cgo(line, line_name)

    centers = calculateCenters(dot1, dot2)

    showSphere(centers)



findSphereCenters()

