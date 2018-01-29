from Pizzicato.views.utils import PrintablesImportFileView
from Pizzicato.controllers import PizzicatoController
from Pizzicato import text

from PyQt4 import QtGui, QtCore
from StringOperations import find_closer_string_in_list
import os


class ImportPrintablesFiles(QtGui.QWidget):

    def __init__(self, files, piece, parent):
        super(ImportPrintablesFiles, self).__init__(parent, QtCore.Qt.Window)
        self._files = files
        self._piece = piece
        self._band = piece.band
        self.configure()
        self.initUI()

    def configure(self):
        self.setWindowTitle(text.DIALOG_IMPORT_PRINTABLES)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self):
        self._layout = QtGui.QVBoxLayout(self)
        self._printables = self._create_printable_widgets()
        self._scroll_area = self._create_scroll_area()
        self._buttons_layout = self._create_buttons_layout()

        self._layout.addWidget(self._scroll_area)
        self._layout.addLayout(self._buttons_layout)

    def _create_printable_widgets(self):
        widgets = []
        instruments = self._band.instruments

        for f in self._files:
            instrument = find_closer_string_in_list(
                os.path.basename(f), instruments)
            widget = PrintablesImportFileView(f)
            widget.fill_combobox_and_set_text(instruments, instrument)
            widgets.append(widget)

        return widgets

    def _create_scroll_area(self):
        widget = QtGui.QWidget()
        widget.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        layout = QtGui.QVBoxLayout(widget)
        layout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        for printable in self._printables:
            layout.addWidget(printable)
        layout.addStretch(1)

        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(widget)
        return scroll_area

    def _create_buttons_layout(self):
        accept = QtGui.QPushButton(text.IMPORT)
        accept.clicked.connect(self.on_accept_clicked)
        cancel = QtGui.QPushButton(text.CANCEL)
        cancel.clicked.connect(self.close)

        layout = QtGui.QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(accept)
        layout.addWidget(cancel)
        return layout

    def on_accept_clicked(self):
        instruments = [
            (printable.path(), printable.instrument())
            for printable in self._printables]
        PizzicatoController.add_printables_files(instruments, self._piece)
        self.close()


class AboutBoxView(QtGui.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.configure()
        self.initUI()

    def configure(self):
        self.setWindowTitle(text.DIALOG_ABOUT_TITLE)

    def initUI(self):
        pass