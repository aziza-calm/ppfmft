import os
import tempfile
import pymol
import subprocess
from pymol.Qt.utils import loadUi
from pymol.Qt import QtWidgets


def set_object_list(combobox):
    objects = pymol.cmd.get_names('objects')
    combobox.clear()
    combobox.addItems(objects)
    combobox.setCurrentIndex(len(objects) - 1)
    return combobox


class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        uifile = os.path.join(os.path.dirname(__file__), 'dock_window.ui')
        form = loadUi(uifile, self)
        self.ligand_combobox = set_object_list(self.ligand_combobox)
        self.receptor_combobox = set_object_list(self.receptor_combobox)
        self.button_dock.clicked.connect(self.dock_pressed)
        self.settings_button.clicked.connect(self.settings_pressed)

    def dock_pressed(self):
        print("Dock button pressed")
        recname = self.receptor_combobox.currentText()
        ligname = self.ligand_combobox.currentText()
        # Creating a temporary directory
        tmpdir = tempfile.mkdtemp()

        # Making copies of receptor and ligand into tmpdir
        rec = tmpdir + "/receptor.pdb"
        pymol.cmd.save(rec, recname)
        lig = tmpdir + "/ligand.pdb"
        pymol.cmd.save(lig, ligname)

        # Preparations for running fmft (creating a string command for Popen)
        dirname = "/home/aziza/Documents/sciense/fmft_suite"
        srcfmft = dirname + "/install-local/bin/fmft_dock.py"
        wei = dirname + "/install-local/bin/prms/fmft_weights_ei.txt"
        NRES = 1000
        fmftcmd = ["python", srcfmft, "--nres", str(NRES), rec, lig, wei]
        print(fmftcmd)
        # Run!
        p = subprocess.Popen(fmftcmd, cwd=tmpdir)
        rc = p.returncode
        if rc is not None:
            print("The process seems to finish")
            print("Maybe you can find something in " + tmpdir)
        else:
            print("FMFT failed")

    def settings_pressed(self):
        print("Settings button pressed")
