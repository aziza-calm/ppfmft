def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('ppfmft2', run_plugin_gui)


def run_plugin_gui():
    import os
    import sys
    sys.path.append(os.path.dirname(__file__))
    from main_window import MainWindow

    global main_window

    main_window = MainWindow()
    main_window.show()
