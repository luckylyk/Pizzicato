

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
from PyQt4 import QtGui
import sys


def main():
    my_application = QtGui.QApplication(sys.argv)
    main_window = MainView(context, parent=None)
    main_window.show()
    my_application.setStyle('Plastique')
    my_application.exec_()


if __name__ == '__main__':
    main()
