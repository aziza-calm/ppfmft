import json
import os
import glob
import numpy as np

with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/1gxd_2/clusters.000.0.0.json') as json_file:
    clusters = json.load(json_file)

centers = clusters['clusters']

with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/1gxd_2/ligs_in.json') as json_file:
    ligs = json.load(json_file)

path = "/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/1gxd_1/"
ligs.extend(glob.glob(path + "*.pdb"))

def get_energy(lig):
    ft_file = os.path.dirname(lig) + "/ft.000.0.0"
    ft_data = np.loadtxt(ft_file)
    num = int(os.path.basename(lig).split('.')[1])
    return ft_data[centers[num]['center'], 4]

to_sort = []
for lig in ligs:
    dic = {}
    dic['path'] = lig
    dic['energy'] = get_energy(lig)
    to_sort.append(dic)

to_sort = sorted(to_sort, key = lambda i: i['energy'])
with open('ligs_sorted.json', 'w') as outfile:
    json.dump(to_sort, outfile)

for i in range(len(to_sort)):
    print(to_sort[i])