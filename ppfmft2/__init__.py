import os


def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('ppfmft2', run_plugin_gui)


dialog = None


def run_plugin_gui():
    global dialog
    dialog = make_dialog()
    dialog.show()


def make_dialog():
    from pymol.Qt import QtWidgets
    from pymol.Qt.utils import loadUi

    dialog = QtWidgets.QDialog()

    uifile = os.path.join(os.path.dirname(__file__), 'dock_window.ui')
    form = loadUi(uifile, dialog)

    def dock():
        print("Dock button was pressed")

    form.button_dock.clicked.connect(dock)

    return dialog
