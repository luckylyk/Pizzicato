from Pizzicato import text
from Pizzicato.model import Piece, AudioFile, Band
from Pizzicato.preferences import PizzicatoPreferences, PizzicatoEnums, icons
from Pizzicato.controllers import PizzicatoController
from Pizzicato.functions import open_folder_in_explorer, start_file
from Pizzicato.views.dialogs import (
    ImportPrintablesFiles, PreferencesEditor,
    PrintablesMerger, AudioZipper)
from Pizzicato.views.utils import (
    LineEditAsLabel, FloatEditLineView,
    warning, PrintablesImportFileView)
from Pizzicato.views.menus import MainMenuBar, FilesViewContextMenu
from Pizzicato.views.tables import (
    BandsComboBoxView, BandsTableModel, PieceListModel, PieceListView,
    FilesTableView, FilesAbstractTableModel, WipFilesTableView,
    AudioFilesTableModel)

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import os


class PiecesViewWidget(QtWidgets.QWidget):
    pieceSelected = QtCore.pyqtSignal(Piece)
    bandSelected = QtCore.pyqtSignal(Band)

    def __init__(self, context, parent=None):
        super(PiecesViewWidget, self).__init__(parent)
        self._context = context
        self._current_band = None
        self.initUI()

    def initUI(self):
        self._set_widget_setting()

        self._actions = self._create_actions()

        self._bands_model = BandsTableModel(self._context.bands, parent=self)
        self._bands_combo = BandsComboBoxView(self._bands_model, parent=self)
        self._bands_combo.currentIndexChanged.connect(self.on_band_changed)

        self._bands_actions_bar = self._create_band_actions_bar()
        self._group_band = self._create_group_bands()

        self._piece_model = PieceListModel(parent=self)
        self._piece_model.edited.connect(self.on_piece_selected)
        self._piece_model.set_bands(self._bands_combo.get_current_band())
        self._piece_list_view = PieceListView(self._piece_model, parent=self)
        self._piece_list_selection_model = self._piece_list_view.selectionModel()
        self._piece_list_selection_model.selectionChanged.connect(
            self.on_piece_selected)
        self._piece_list_actions_bar = self._piece_list_create_actions_bar()
        self._piece_list_view_widget = self._create_piece_list_view_widget()

        self._band_wip_list = WipFilesTableView(self)
        self._tab_lists = self._create_tab_lists()
        self._layout = self._create_layout()

    def _set_widget_setting(self):
        self.setContentsMargins(0, 0, 0, 0)

    def _create_band_actions_bar(self):
        bar = QtWidgets.QMenuBar(self)
        bar.addAction(self._actions['create band'])
        bar.addAction(self._actions['rename band'])
        bar.addAction(self._actions['delete band'])
        bar.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        return bar

    def _create_piece_list_view_widget(self):
        widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._piece_list_view)
        layout.addWidget(self._piece_list_actions_bar)
        return widget

    def _create_actions(self):
        actions = {}

        actions['create piece'] = QtWidgets.QAction(
            self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon), '', self)
        actions['create piece'].triggered.connect(self.on_new_triggered)
        actions['create piece'].setShortcut(QtGui.QKeySequence.New)

        actions['delete piece'] = QtWidgets.QAction(
            self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon), '', self)
        actions['delete piece'].triggered.connect(
            self.on_piece_deleted_triggered)
        actions['delete piece'].setShortcut(QtGui.QKeySequence.Delete)

        actions['open piece in explorer'] = QtWidgets.QAction(
            self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon), '', self)
        actions['open piece in explorer'].triggered.connect(
            self.on_open_piece_in_explorer_triggered)
        actions['open piece in explorer'].setShortcut(QtGui.QKeySequence.Open)

        actions['create band'] = QtWidgets.QAction(
            self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon), '', self)
        actions['create band'].triggered.connect(
            self.on_open_add_band_triggered)

        actions['rename band'] = QtWidgets.QAction(icons.rename, '', self)
        actions['rename band'].triggered.connect(
            self.on_open_rename_band_triggered)

        actions['delete band'] = QtWidgets.QAction(
            self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon), '', self)
        actions['delete band'].triggered.connect(
            self.on_open_delete_band_triggered)

        return actions

    def _piece_list_create_actions_bar(self):
        bar = QtWidgets.QMenuBar(self)
        bar.addAction(self._actions['create piece'])
        bar.addAction(self._actions['open piece in explorer'])
        bar.addAction(self._actions['delete piece'])
        return bar

    def _create_tab_lists(self):
        tab = QtWidgets.QTabWidget(self)
        tab.addTab(self._piece_list_view_widget, text.FINALS)
        tab.addTab(self._band_wip_list, text.WORK_IN_PROGRESS)
        return tab

    def _create_group_bands(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self._bands_combo)
        layout.addWidget(self._bands_actions_bar)
        group = QtWidgets.QGroupBox(text.SELECT_BAND)
        group.setLayout(layout)
        return group

    def _create_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._group_band)
        layout.addWidget(self._tab_lists)

    def get_current_selected_piece(self):
        return [
            self._piece_model.get_piece(index.row())
            for index in self._piece_list_selection_model.selectedIndexes()][0]

    def get_current_band(self):
        return self._current_band

    def on_band_changed(self):
        band = self._bands_combo.get_current_band()
        self._piece_model.set_bands(band)
        self._band_wip_list.set_root_path(band.wip_folder)
        self._current_band = band
        self.bandSelected.emit(band)

    def on_new_triggered(self):
        line = FloatEditLineView(text.NEW_PIECE, self)
        line.setGeometry(
            self.mapToGlobal(self._piece_list_view.pos()).x() + 5,
            self.mapToGlobal(self._piece_list_view.pos()).y() +
            self._piece_list_view.height() + 70,
            self._piece_list_view.width() - 5,
            20)
        line.accepted.connect(self.create_piece)
        line.show()

    def create_piece(self, name):
        PizzicatoController.create_piece(
            self._bands_combo.get_current_band(), name)

    def rename_band(self, name):
        PizzicatoController.rename_band(
            self._bands_combo.get_current_band(), name)

    def on_open_piece_in_explorer_triggered(self):
        open_folder_in_explorer(self.get_current_selected_piece().path)

    def on_piece_deleted_triggered(self):
        msg = warning(text.DELETE_WARNING, question=True)
        if msg == QtWidgets.QMessageBox.Cancel:
            return
        PizzicatoController.remove_piece(self.get_current_selected_piece())

    def on_piece_selected(self, indexes=None):
        if indexes is None:
            piece = self.get_current_selected_piece()
        else:
            piece = [
                self._piece_model.get_piece(index.row())
                for index in indexes.indexes()][0]

        self.pieceSelected.emit(piece)

    def on_open_add_band_triggered(self):
        line = FloatEditLineView(text.NEW_BAND, self)
        line.setGeometry(
            self.mapToGlobal(self._bands_combo.pos()).x(),
            self.mapToGlobal(self._bands_combo.pos()).y(),
            self._bands_combo.width(),
            self._bands_combo.height())
        line.accepted.connect(PizzicatoController.create_band)
        line.show()

    def on_open_rename_band_triggered(self):
        line = FloatEditLineView(self._current_band.name, self)
        line.setGeometry(
            self.mapToGlobal(self._bands_combo.pos()).x(),
            self.mapToGlobal(self._bands_combo.pos()).y(),
            self._bands_combo.width(),
            self._bands_combo.height())
        line.accepted.connect(self.rename_band)
        line.show()

    def on_open_delete_band_triggered(self):
        msg = warning(text.DELETE_WARNING, question=True)
        if msg == QtWidgets.QMessageBox.Cancel:
            return
        PizzicatoController.remove_band(self.get_current_band())


#  Refactorise a bit
class PiecePropertiesView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PiecePropertiesView, self).__init__(parent)
        self._piece = None
        self._is_setting_moment = False
        self.initUI()

    def initUI(self):
        self._set_settings()
        self._title = QtWidgets.QLabel(self._get_title_label())
        self._infos_group = self._create_infos_group()

        self._layout = self._create_layout(self)
#         self._layout.addWidget(self._title)
        self._layout.addWidget(self._infos_group)

    def _get_title_label(self):
        piece = self._piece
        title = piece.title if piece != None else text.NO_PIECE_SELECTED
        return '<div align="center"><h1><strong>{}</strong></h1>'.format(title)

    def _create_infos_group(self):
        group = QtWidgets.QGroupBox(text.PIECE_INFOS)

        group.author = LineEditAsLabel('', parent=self)
        group.author.textEdited.connect(self.on_properties_edited)
        group.arranger = LineEditAsLabel('', parent=self)
        group.arranger.textEdited.connect(self.on_properties_edited)
        group.style = LineEditAsLabel('', parent=self)
        group.style.textEdited.connect(self.on_properties_edited)
        group.solists = LineEditAsLabel('', parent=self)
        group.solists.textEdited.connect(self.on_properties_edited)
        group.comment = QtWidgets.QTextEdit(parent=self)
        group.comment.textChanged.connect(self.on_properties_edited)

        layout_up = QtWidgets.QFormLayout()
        layout_up.addRow(self._title)
        layout_up.addRow(text.AUTHOR + ' :', group.author)
        layout_up.addRow(text.ARRANGER + ' :', group.arranger)
        layout_up.addRow(text.STYLE + ' :', group.style)
        layout_up.addRow(text.SOLIST + ' :', group.solists)
        layout_up.addRow(text.COMMENT + ' :', group.comment)

        group.tempi = self._create_combo_box(PizzicatoEnums.TEMPI)
        group.tempi.currentIndexChanged.connect(self.on_properties_edited)
        group.mood = self._create_combo_box(PizzicatoEnums.MOODS)
        group.mood.currentIndexChanged.connect(self.on_properties_edited)
        group.priority = self._create_combo_box(PizzicatoEnums.PRIORITY)
        group.priority.currentIndexChanged.connect(self.on_properties_edited)

        layout_mid = QtWidgets.QHBoxLayout()
        layout_mid.addWidget(QtWidgets.QLabel(text.TEMPO + ' :'))
        layout_mid.addWidget(group.tempi)
        layout_mid.addStretch(1)
        layout_mid.addWidget(QtWidgets.QLabel(text.MOOD + ' :'))
        layout_mid.addWidget(group.mood)
        layout_mid.addStretch(1)
        layout_mid.addWidget(QtWidgets.QLabel(text.PRIORITY + ' :'))
        layout_mid.addWidget(group.priority)

        group.save = QtWidgets.QPushButton(text.SAVE)
        group.save.setEnabled(False)
        group.save.clicked.connect(self.on_save_clicked)

        layout_down = QtWidgets.QHBoxLayout()
        layout_down.addStretch(1)
        layout_down.addWidget(group.save)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layout_up)
        layout.addLayout(layout_mid)
        layout.addLayout(layout_down)

        group.setLayout(layout)
        return group

    def _set_settings(self):
        if not self._piece:
            self.setEnabled(False)

    def _create_layout(self, parent):
        layout = QtWidgets.QVBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def _create_combo_box(self, items):
        combobox = QtWidgets.QComboBox()
        combobox.addItems(items)
        return combobox

    def _set_widget_setting(self):
        self.setContentsMargins(0, 0, 0, 0)

    def _set_piece_properties(self):
        self._piece.set_author(self._infos_group.author.text())
        self._piece.set_arranger(self._infos_group.arranger.text())
        self._piece.set_style(self._infos_group.style.text())
        self._piece.set_solists(self._infos_group.solists.text().split(', '))
        self._piece.set_priority(self._infos_group.priority.currentIndex())
        self._piece.set_tempo(self._infos_group.tempi.currentText())
        self._piece.set_mood(self._infos_group.mood.currentIndex())
        self._piece.set_comment(self._infos_group.comment.toHtml())

    def set_piece(self, piece):
        self._is_setting_moment = True
        if self._piece is not None:
            self._set_piece_properties()
        self._infos_group.tempi.setCurrentIndex(
            [i for i, tempo in enumerate(PizzicatoEnums.TEMPI)
             if tempo == str(piece.tempo)][0])
        self._infos_group.author.setText(piece.author)
        self._infos_group.arranger.setText(piece.arranger)
        self._infos_group.style.setText(piece.style)
        self._infos_group.solists.setText(', '.join(piece.solists))
        self._infos_group.priority.setCurrentIndex(piece.priority)
        self._infos_group.mood.setCurrentIndex(piece.mood)
        self._infos_group.save.setEnabled(not piece.is_saved())
        self._infos_group.comment.setHtml(piece.comment)
        self._piece = piece
        self._title.setText(self._get_title_label())
        if not self.isEnabled():
            self.setEnabled(True)
        self._is_setting_moment = False

    def on_properties_edited(self):
        if self._is_setting_moment:
            return
        self._piece.set_unsaved()
        self._infos_group.save.setEnabled(True)

    def on_save_clicked(self):
        self._set_piece_properties()
        self._piece.save_properties()
        self._infos_group.save.setEnabled(False)


class PrintableFilesView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(PrintableFilesView, self).__init__(parent)
        self._piece = None
        self.initUI()

    def initUI(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._printable_files_model = FilesAbstractTableModel(
            columns=[
                (text.INSTRUMENT, 'instrument'), (text.TYPE, 'type'),
                (text.PATH, 'path')],
            parent=self)
        self._printable_files_table = FilesTableView(
            model=self._printable_files_model,
            parent=self, menu=FilesViewContextMenu(self))
        self._printable_files_table.set_filters(
            PizzicatoPreferences.PRINTABLES_SUPPORTED_EXTENSIONS)
        self._printable_files_table.droppedFiles.connect(self.on_files_dropped)

        self._layout.addWidget(self._printable_files_table)

        PizzicatoController.append_printables_model(
            self._printable_files_model)

    def set_piece(self, piece):
        self._piece = piece
        self._printable_files_model.set_datas(
            piece.get_printable_files())

    def on_files_dropped(self, files):
        dialog = ImportPrintablesFiles(files, self._piece, parent=self)
        dialog.show()


class AudioFilesView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(AudioFilesView, self).__init__(parent)
        self._piece = None
        self.initUI()

    def initUI(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._audio_files_model = AudioFilesTableModel(
            columns=[
                (text.CATEGORIE, 'categorie'), (text.NAME, 'name'),
                (text.EXTENTION, 'ext'),
                (text.PATH, 'path')],
            parent=self)
        self._audio_files_table = FilesTableView(
            model=self._audio_files_model,
            parent=self,
            menu=FilesViewContextMenu(self))
        self._audio_files_table.droppedFiles.connect(self.on_dropped_files)
        # self._sound_reader = SoundReader()
        self._audio_files_table.selectionIsChanged.connect(
            self._selectionChanged)
        self._audio_files_table.set_filters(
            PizzicatoPreferences.AUDIOS_SUPPORTED_EXTENSIONS)

        self._layout.addWidget(self._audio_files_table)
        # self._layout.addWidget(self._sound_reader)

    def _selectionChanged(self):
        data = self._audio_files_table.get_selected_data()
        # self._sound_reader.set_music_file(data)

    def set_piece(self, piece):
        self._piece = piece
        self._audio_files_model.set_datas(piece.get_audio_files())
        self._audio_files_table.update()

    def on_dropped_files(self, files):
        PizzicatoController.import_audios_files(files, self._piece)
        self.set_piece(self._piece)


class EditableFilesView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(EditableFilesView, self).__init__(parent)
        self._piece = None
        self.initUI()

    def initUI(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._editable_files_model = FilesAbstractTableModel(
            columns=[
                (text.FILE, 'file'), (text.DESCRIPTION, 'description'),
                (text.PROGRAM, 'program')],
            parent=self)
        self._editable_files_table = FilesTableView(
            model=self._editable_files_model,
            parent=self,
            menu=FilesViewContextMenu(self))
        self._editable_files_table.droppedFiles.connect(self.on_dropped_files)
        self._editable_files_table.set_filters(
            PizzicatoPreferences.EDITABLES_SUPPORTED_EXTENSIONS)

        self._layout.addWidget(self._editable_files_table)

    def set_piece(self, piece):
        self._piece = piece
        self._editable_files_model.set_datas(piece.get_editable_files())
        self._editable_files_table.update()

    def on_dropped_files(self, files):
        PizzicatoController.import_editables_files(files, self._piece)
        self.set_piece(self._piece)
