from Bio.PDB import *

molec = '/home/aziza/Downloads/000000_nmin.pdb'

class ABChainSelect(Select):
    def accept_chain(self, chain):
        if chain.get_id() == 'A':
            return 1
        else:
            return 0

class CDChainSelect(Select):
    def accept_chain(self, chain):
        if chain.get_id() =='B':
            return 1
        else:
            return 0


parser = PDBParser()
structure = parser.get_structure('mymol', molec)

ab = PDBIO()
ab.set_structure(structure)
ab.save('vita_r.pdb', ABChainSelect())

cd = PDBIO()
cd.set_structure(structure)
cd.save('vita_l.pdb', CDChainSelect())