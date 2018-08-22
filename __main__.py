import sys
import os

_current_dir = os.path.dirname(os.path.realpath(__file__))
APP_FOLDER = os.path.dirname(_current_dir)
sys.path.insert(0, APP_FOLDER)
sys.path.insert(0, os.path.join(APP_FOLDER, 'PyQt'))


# load preferences
from Pizzicato.preferences import PizzicatoPreferences
# PizzicatoPreferences.load(PizzicatoPreferences.PREFS_FILE_PATH)

# load context and set controller
from Pizzicato.model import PizzicatoContext
from Pizzicato.controllers import PizzicatoController
context = PizzicatoContext(PizzicatoPreferences.CURRENT_WORKING_DIR)
PizzicatoController.set_context(context)

# load views
from Pizzicato.views.main import MainView

# external import
from PyQt5 import QtWidgets


def main():
    my_application = QtWidgets.QApplication(sys.argv)
    main_window = MainView(context, parent=None)
    main_window.show()
    my_application.setStyle('Plastique')
    my_application.exec_()


if __name__ == '__main__':
    main()
