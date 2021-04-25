import os
import tempfile

from qt_wrapper import QtWidgets, QtCore, WITH_PYMOL, uic


def fmft_path():
    if WITH_PYMOL:
        user_path = os.path.expanduser("~")
        fmftpath = "/home/aziza/Documents/sciense/fmft_suite"
        # fmftpath = pymol.plugins.pref_get("FMFT_PATH", d="/home/aziza/Documents/sciense/fmft_suite")
    return fmftpath


def dialog(message):
    qdialog = QtWidgets.QMessageBox()
    qdialog.setIcon(QtWidgets.QMessageBox.Question)
    qdialog.setWindowTitle("Warning")
    qdialog.setText(message)
    qdialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
    return qdialog.exec_() == QtWidgets.QMessageBox.Ok


class MainWindow(QtWidgets.QDialog):
    PDB_FILE_WIDGETS = ('pdbFileLabel', 'pdbFileSelector')
    PYMOL_OBJECT_WIDGETS = ('pymolObjectLabel', 'pymolObjectCombo', 'refreshObjectsButton')

    def __init__(self, settings):
        super(MainWindow, self).__init__()
        uifile = os.path.join(os.path.dirname(__file__), 'main_window.ui')
        uic.loadUi(uifile, self)
        self.setup_objects_list()
        self.setup_radio_buttons()
        self.settings = settings
        self.button_dock.clicked.connect(self.dock_pressed)
        self.settings_button.clicked.connect(self.settings_pressed)
        self.p = None

    def setup_objects_list(self):
        if WITH_PYMOL:
            import pymol
            objects = pymol.cmd.get_names('objects')
            self.ligand_combobox.clear()
            self.ligand_combobox.addItems(objects)
            self.ligand_combobox.setCurrentIndex(len(objects) - 1)
            self.receptor_combobox.clear()
            self.receptor_combobox.addItems(objects)
            self.receptor_combobox.setCurrentIndex(len(objects) - 1)
        else:
            self.pymolObjectRadio.setEnabled(False)

    def setup_radio_buttons(self):
        if WITH_PYMOL:
            self.pdbFileRadio.setChecked(False)
            self.pymolObjectRadio.setChecked(True)
        else:
            self.pdbFileRadio.setChecked(True)
            self.pymolObjectRadio.setChecked(False)

    def message(self, s):
        self.text.appendPlainText(s)

    def dock_pressed(self):
        # Check if translation matrices are precomputed
        print(self.settings.fmftpath)
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
        print(tmpdir)
        # Making copies of receptor and ligand into tmpdir
        if WITH_PYMOL:
            rec = tmpdir + "/receptor.pdb"
            # pymol.cmd.save(rec, recname)
            print("receptor saved in " + rec)
            lig = tmpdir + "/ligand.pdb"
            # pymol.cmd.save(lig, ligname)
            print("ligand saved in " + lig)
        else:
            rec = "/home/aziza/1avx_r_nmin.pdb"
            lig = "/home/aziza/1avx_l_nmin.pdb"
            print(lig)
        if self.p is None:  # No process running.
            print("Process is about to start\n")
            self.message("Executing process")
            self.p = QtCore.QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.
            # Preparations for running fmft (creating a string command for Popen)
            dirname = "/home/aziza/Documents/sciense/fmft_suite"
            srcfmft = dirname + "/install-local/bin/fmft_dock.py"
            wei = dirname + "/install-local/bin/prms/fmft_weights_ei.txt"
            NRES = 1000
            fmftcmd = [srcfmft, "--nres", str(NRES), rec, lig, wei]
            print(fmftcmd)
            self.p.start("python", fmftcmd)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QtCore.QProcess.NotRunning: 'Not running',
            QtCore.QProcess.Starting: 'Starting',
            QtCore.QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.p = None

    def settings_pressed(self):
        self.settings.show()
