from Pizzicato import text
from Pizzicato.preferences import PizzicatoPreferences
from Pizzicato.views.widgets import (
    PiecesViewWidget, PiecePropertiesView, EditableFilesView,
    PrintableFilesView, AudioFilesView, MainMenuBar)
from Pizzicato.views.dialogs import PreferencesEditor

from PyQt5 import QtWidgets, QtWidgets, QtCore


class MainView(QtWidgets.QWidget):

    def __init__(self, context, parent=None):
        super(MainView, self).__init__(parent)
        self._context = context
        self.initUI()

    def initUI(self):
        self.setWindowTitle(text.MAIN_WINDOW_TITLE)

        self._main_menu_bar = MainMenuBar()

        self._left_widget = PiecesViewWidget(self._context, self)
        self._middle_widget = self._create_middle_widget()
        self._connect_widgets()

        self._splitter = QtWidgets.QSplitter()
        self._splitter.addWidget(self._left_widget)
        self._splitter.addWidget(self._middle_widget)

        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._main_layout.addWidget(self._splitter)
        self._main_layout.addWidget(self._main_menu_bar)

    def _create_middle_widget(self):
        widget = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        widget.piece_properties_view = PiecePropertiesView(self)

        widget.splitter_files = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        widget.editables_files_view = EditableFilesView(self)
        widget.music_files_view = AudioFilesView(self)
        widget.splitter_files.addWidget(widget.editables_files_view)
        widget.splitter_files.addWidget(widget.music_files_view)

        widget.printable_files_view = PrintableFilesView(self)

        widget.tab = QtWidgets.QTabWidget(self)
        widget.tab.addTab(widget.splitter_files, text.EDITABLES_AND_AUDIOS)
        widget.tab.addTab(widget.printable_files_view, text.PRINTABLES)

        widget.addWidget(widget.piece_properties_view)
        widget.addWidget(widget.tab)

        widget.setSizes([318, 374])
        return widget

    def _connect_widgets(self):
        self._left_widget.pieceSelected.connect(self._set_piece)

    def _set_piece(self, piece):
        self._middle_widget.music_files_view.set_piece(piece)
        self._middle_widget.editables_files_view.set_piece(piece)
        self._middle_widget.piece_properties_view.set_piece(piece)
        self._middle_widget.printable_files_view.set_piece(piece)
