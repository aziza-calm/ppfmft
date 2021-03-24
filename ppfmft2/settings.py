import os
import pymol
from pymol.Qt.utils import loadUi
from pymol.Qt import QtWidgets


class Settings(QtWidgets.QMainWindow):
    def __init__(self):
        super(Settings, self).__init__()
        uifile = os.path.join(os.path.dirname(__file__), 'settings.ui')
        loadUi(uifile, self)
        self.fmftpath = pymol.plugins.pref_get("FMFT_PATH", d="/home/aziza/Documents/sciense/fmft_suite")
        self.sblupath = pymol.plugins.pref_get("SBLU_PATH", d="/home/aziza/.local/bin/sblu")
