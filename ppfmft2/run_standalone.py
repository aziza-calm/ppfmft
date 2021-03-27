import sys
from qt_wrapper import QtWidgets
from settings import Settings
from main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    settings = Settings()
    main_window = MainWindow(settings)

    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
