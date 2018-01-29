from PyQt4 import QtGui, QtCore
from Pizzicato.preferences import PizzicatoPreferences, PizzicatoEnums, icons
from Pizzicato.model import Piece, AudioFile, Band
from Pizzicato.functions import open_folder_in_explorer, start_file
from Pizzicato.controllers import PizzicatoController
from Pizzicato.views.dialogs.merge import PrintablesMerger, AudioZipper
from Pizzicato.views.dialogs.preferences import PreferencesEditor
from Pizzicato import text
import os
from functools import partial


class FilesViewContextMenu(QtGui.QMenu):

    def __init__(self, parent=None):
        super(FilesViewContextMenu, self).__init__(parent)
        self._file = None
        self._style = self.style()

    def set_abstract_file(self, abstract_file):
        self._file = abstract_file
        self.initUI()

    def initUI(self):
        self.clear()
        self._actions = self._get_actions()
        self.addActions(self._actions)
        if isinstance(self._file, AudioFile):
            self._menu_music_type = self._create_music_type_menu()
            self.addSeparator()
            self.addMenu(self._menu_music_type)

    def _get_actions(self):
        style = self.style()
        _open = QtGui.QAction('open', self)
        _open.setIcon(style.standardIcon(QtGui.QStyle.SP_DialogOpenButton))
        _open.triggered.connect(self.on_open_triggered)

        _open_folder = QtGui.QAction('open folder', self)
        _open_folder.setIcon(
            style.standardIcon(QtGui.QStyle.SP_DialogOpenButton))
        _open_folder.triggered.connect(self.on_open_folder_triggered)

        _delete = QtGui.QAction('delete', self)

        return _open, _open_folder, _delete

    def _create_music_type_menu(self):

        menu = QtGui.QMenu('Change Type', self)
        menu.original = QtGui.QAction('Original', self)
        menu.original.triggered.connect(
            partial(self.on_music_type_changed, 'original'))
        menu.maquette = QtGui.QAction('Maquette', self)
        menu.maquette.triggered.connect(
            partial(self.on_music_type_changed, 'maquette'))
        menu.divers = QtGui.QAction('Divers', self)
        menu.divers.triggered.connect(
            partial(self.on_music_type_changed, 'divers'))
        menu.addActions([menu.original, menu.maquette, menu.divers])
        return menu

    def on_open_triggered(self):
        start_file(self._file)

    def on_open_folder_triggered(self):
        open_folder_in_explorer(os.path.dirname(self._file.path))

    def on_music_type_changed(self, file_categorie):
        PizzicatoController.set_audio_file_categorie(
            self._file, file_categorie)


class MainMenuBar(QtGui.QWidget):
    BUTTON_SIZE = QtCore.QSize(50, 50)

    def __init__(self, parent=None):
        super(MainMenuBar, self).__init__()
        self.initUI()

    def initUI(self):
        self._zip = self._create_button(
            icons.zip, self.on_zip_clicked)
        self._merge = self._create_button(
            icons.merge2, self.on_merge_clicked)
        self._preferences = self._create_button(
            icons.preferences, self.on_preferences_clicked)
        self._about = self._create_button(
            icons.about, self.on_about_clicked)

        self._layout = QtGui.QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._fill_layout()

    def _fill_layout(self):
        self._layout.addWidget(self._zip)
        self._layout.addWidget(self._merge)
        self._layout.addWidget(self._preferences)
        self._layout.addWidget(self._about)
        self._layout.addStretch(1)

    def _create_button(self, icon, function):
        button = QtGui.QPushButton(icon, '')
        button.clicked.connect(function)
        button.setFlat(True)
        button.resize(self.BUTTON_SIZE)
        button.setIconSize(self.BUTTON_SIZE)
        return button

    def on_merge_clicked(self):
        merge = PrintablesMerger(self)
        merge.setWindowTitle(text.DIALOG_PDF_MERGER)
        merge.show()

    def on_about_clicked(self):
        pass

    def on_zip_clicked(self):
        zipper = AudioZipper(self)
        zipper.setWindowTitle(text.FILE_DIALOG_SAVE_ZIP_FILES)
        zipper.show()

    def on_preferences_clicked(self):
        preferences = PreferencesEditor()
        preferences.show()
