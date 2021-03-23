import os
from pymol.Qt.utils import loadUi
from pymol.Qt import QtGui, QtCore, QtWidgets
from pymol.Qt.utils import (getSaveFileNameWithExt, UpdateLock, WidgetMenu,
                            PopupOnException,
                            connectFontContextMenu, getMonospaceFont)


class MainWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        uifile = os.path.join(os.path.dirname(__file__), 'dock_window.ui')
        form = loadUi(uifile, self)
        self.ligand_combobox = self.set_object_list(self.ligand_combobox)
        self.receptor_combobox = self.set_object_list(self.receptor_combobox)

    def set_object_list(self, combobox):
        import pymol
        objects = pymol.cmd.get_names('objects')
        combobox.clear()
        combobox.addItems(objects)
        combobox.setCurrentIndex(len(objects) - 1)
        return combobox
