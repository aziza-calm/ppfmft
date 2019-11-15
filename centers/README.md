The main file is `find_remote.py`. It computes most remote CA atoms in molecule, writes its coordinates in remote_dots.json, computes centers and writes them in centers.json.

`find_remote.ipynb` is a copy of `find_remote.py`, but with markdown explanations of different parts (not included yet)

`test_pymol.py` - draws the spheres in pymol. The centers of the spheres are taken from centers.json.

`check_models.py` - checks if the model has at least one atom inside the sphere, writes the list of such models in ligs_in.json.

All other files are not so important, but still useful.

`divide_mol.py` - divides molecule (structure) in separate chains.

`load_ligs_in.py` - loads in pymol all ligands listed in ligs_in.json

`load_ligs.py` - loads in pymol all pdbs of selected directory.

`box-pymol.py` - shows the axis box in which the selection is enclosed.
