from pymol import cmd
import glob
import os

path = "/home/aziza/Downloads/basa/pymol/ppfmft/centers/mol_test/1oph_only_center/"
ligs = glob.glob(path + "*.pdb")

for lig in ligs:
    cmd.load(lig, os.path.basename(lig))