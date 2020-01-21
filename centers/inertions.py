from pymol import cmd

molec = "/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/1avx_l_nmin.pdb"

cmd.load(molec, 'molec')
cmd.pseudoatom('com', pos=cmd.centerofmass('molec'))
ceom = cmd.centerofmass('molec')
# cmd.centerofmass()

# def inert(name):
#     # print(name)
#     print(cmd.get_distance(atom1='com', atom2=name))

# myspace = {'inert': inert}
# print(cmd.iterate('molec', 'inert(name)', space=myspace))

atoms = cmd.get_model('molec')
iner = {'xx': 0, 'yy': 0, 'zz': 0, 'xy': 0, 'yz': 0, 'xz': 0}
for a in atoms.atom:
    if a.name != 'H':
        iner['xx'] += (a.coord[1] - ceom[1])**2 + (a.coord[2] - ceom[2])**2
        iner['yy'] += (a.coord[0] - ceom[0])**2 + (a.coord[2] - ceom[2])**2
        iner['zz'] += (a.coord[0] - ceom[0])**2 + (a.coord[1] - ceom[1])**2
        iner['xy'] += (a.coord[0] - ceom[0])*(a.coord[1] - ceom[1])
        iner['yz'] += (a.coord[1] - ceom[1])*(a.coord[2] - ceom[2])
        iner['xz'] += (a.coord[0] - ceom[0])*(a.coord[2] - ceom[2])

print(iner)