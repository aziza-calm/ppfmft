# ppfmft
maybe one day it will become a plugin for PyMol that runs fmft

Big goals:
1. To make comboboxes show files already uploaded (and maybe changed) in current PyMol session (have no idea for now how to do that, seems to me that there is no way to interact with an existing PyMOL session from the Python interpreter)
2. To make the button run fmft properly (for now it runs fmft with subprocess.Popen, need to think about details)
3. To make it show the docking results in a digestible way (z.B. logparse etc)
