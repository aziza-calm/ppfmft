import json
import os
import glob
import numpy as np

pdb_id = '1oph'

with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/{}_2/clusters.000.0.0.json'.format(pdb_id)) as json_file:
    clusters2 = json.load(json_file)

centers2 = clusters2['clusters']

with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/{}_1/clusters.000.0.0.json'.format(pdb_id)) as json_file:
    clusters1 = json.load(json_file)

centers1 = clusters1['clusters']

with open('/home/aziza/Downloads/basa/pymol/ppfmft/centers/ligs_in_{}_2.json'.format(pdb_id)) as json_file:
    ligs = json.load(json_file)

path = "/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/{}_1/".format(pdb_id)
ligs.extend(glob.glob(path + "*.pdb"))

def get_energy(lig):
    ft_file = os.path.dirname(lig) + "/ft.000.0.0"
    ft_data = np.loadtxt(ft_file)
    num = int(os.path.basename(lig).split('.')[1])
    spl = lig.split('/')
    if int(spl[len(spl) - 2].split('_')[1]) == 2:
        print("2 == {}".format(int(spl[len(spl) - 2].split('_')[1])))
        return ft_data[centers2[num]['center'], 4]
    print("1 == {}".format(int(spl[len(spl) - 2].split('_')[1])))
    print(num)
    return ft_data[centers1[num]['center'], 4]

to_sort = []
for lig in ligs:
    dic = {}
    dic['path'] = lig
    print(lig)
    dic['energy'] = get_energy(lig)
    to_sort.append(dic)

to_sort = sorted(to_sort, key = lambda i: i['energy'])
with open('ligs_sorted_{}.json'.format(pdb_id), 'w') as outfile:
    json.dump(to_sort, outfile)

for i in range(len(to_sort)):
    print(to_sort[i])