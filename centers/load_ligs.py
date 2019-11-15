from pymol import cmd
import glob
import os

path = "/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/1gxd_1/"
ligs = glob.glob(path + "*.pdb")

for lig in ligs:
    cmd.load(lig, os.path.basename(lig))