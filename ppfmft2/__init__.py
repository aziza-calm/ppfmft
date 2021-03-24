def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('ppfmft2', run_plugin_gui)


def run_plugin_gui():
    import os
    import sys
    sys.path.append(os.path.dirname(__file__))
    from main_window import MainWindow
    from settings import Settings

    global main_window

    settings = Settings()
    main_window = MainWindow(settings)
    main_window.show()
