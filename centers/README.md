The main file is `find_remote.py`. It computes most remote CA atoms in molecule, writes its coordinates in remote_dots.json, computes centers and writes them in centers.json.

`find_remote.ipynb` is a copy of `find_remote.py`, but with markdown explanations of different parts (not included yet)

`draw_sphere.py` - draws the spheres in pymol. The centers of the spheres are taken from centers.json.

`check_models.py` - checks if the model has at least one atom inside the sphere, writes the list of such models in ligs_in.json.

`zusammenfassen.py` - creates sorted list of dics with two keys: 'path' and 'energy'. Path is the path to ligand which is inside the sphere, and energy is corresponding energy from ft-file. The list is written in ligs_sorted.json.

`add_rmsd.py` - adds one more key to the above mentioned list: 'rmsd'. And writes updated list in sorted_with_rmsd.json.

All other files are not so important, but still useful.

`divide_mol.py` - divides molecule (structure) in separate chains.

`load_ligs_in.py` - loads in pymol all ligands listed in ligs_in.json

`load_ligs.py` - loads in pymol all pdbs of selected directory.

`box-pymol.py` - shows the axis box in which the selection is enclosed.
