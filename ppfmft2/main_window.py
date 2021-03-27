import os
import tempfile
import pymol
import subprocess
from pymol.Qt.utils import loadUi
from qt_wrapper import QtWidgets, QtGui, WITH_PYMOL
import sblu


def fmft_path():
    if WITH_PYMOL:
        user_path = os.path.expanduser("~")
        fmftpath = "/home/aziza/Documents/sciense/fmft_suite"
        # fmftpath = pymol.plugins.pref_get("FMFT_PATH", d="/home/aziza/Documents/sciense/fmft_suite")
    return fmftpath


class MainWindow(QtWidgets.QDialog):
    def __init__(self, settings):
        super(MainWindow, self).__init__()
        uifile = os.path.join(os.path.dirname(__file__), 'main_window.ui')
        loadUi(uifile, self)
        self.ligand_combobox = self.set_object_list(self.ligand_combobox)
        self.receptor_combobox = self.set_object_list(self.receptor_combobox)
        self.settings = settings
        self.button_dock.clicked.connect(self.dock_pressed)
        self.settings_button.clicked.connect(self.settings_pressed)

    def dock_pressed(self):
        # Check if translation matrices are precomputed
        if os.path.exists(self.settings.fmftpath + '/install-local/fmft_data/'):
            if not os.listdir(self.settings.fmftpath + '/install-local/fmft_data/'):
                self.dialog("Couldn't find the appropriate translation matrix file")
                return
        else:
            self.dialog("Couldn't find {your_fmft_path}/install-local/fmft_data/")
            return

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
        self.settings.show()

    @staticmethod
    def set_object_list(combobox):
        if WITH_PYMOL:
            objects = pymol.cmd.get_names('objects')
            combobox.clear()
            combobox.addItems(objects)
            combobox.setCurrentIndex(len(objects) - 1)
        return combobox

    @staticmethod
    def dialog(message):
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Question)
        dialog.setWindowTitle("Warning")
        dialog.setText(message)
        dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        return dialog.exec_() == QtWidgets.QMessageBox.Ok
