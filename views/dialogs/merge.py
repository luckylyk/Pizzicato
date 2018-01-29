from PyQt4 import QtGui, QtCore
from functools import partial
from Pizzicato.controllers import PizzicatoController
from Pizzicato.preferences import PizzicatoPreferences, PizzicatoEnums
from Pizzicato.errors import NotImplementedError
from Pizzicato.views.utils import FitlersView
from Pizzicato import text

###############################################################################
####                             Merger Dialogs                            ####
###############################################################################


class AbstractMergerDialog(QtGui.QWidget):

    def __init__(self, parent=None):
        super(AbstractMergerDialog, self).__init__(parent, QtCore.Qt.Window)
        self.datas = []
        self.initUI()

    def initUI(self):
        self._filters_widgets = self.create_filters()

        self._filters_layout = self._create_filters_layout()
        self._filters_group = QtGui.QGroupBox(text.FILTERS)
        self._filters_group.setLayout(self._filters_layout)

        self._list_model = self.create_list_model()
        self._list_model.edited.connect(self.on_list_model_edited)
        self._list_view = MergerListView()
        self._list_view.setModel(self._list_model)

        self._horizontal_layout = QtGui.QSplitter()
        self._horizontal_layout.addWidget(self._filters_group)
        self._horizontal_layout.addWidget(self._list_view)
        self._horizontal_layout.setContentsMargins(0, 0, 0, 0)

        self._buttons = self.create_buttons()
        self._buttons_layout = self._create_buttons_layout()

        self._layout = QtGui.QVBoxLayout(self)
        self._layout.addWidget(self._horizontal_layout)
        self._layout.addLayout(self._buttons_layout)

    def create_filters(self):
        '''
        Have to reimplant this methods in sub classes
        Have to return list of FiltersView widgets
        created with the methods : self.create_filters_view()
        '''
        raise NotImplementedError(
            'subclass of AbstractMergerDialog need a '
            'create_filters(self) reimplemented')
        return [FitlersView()]

    def create_list_model(self):
        '''
        Have to reimplant this methods in sub classes
        Have to return StandardItemModel
        '''
        raise NotImplementedError(
            'subclass of AbstractMergerDialog need a '
            'create_filters(self) reimplemented')
        return QtGui.QStandardItemModel()

    def create_buttons(self):
        '''
        Have to reimplant this methods in sub classes
        Have to return list of FiltersView widget
        '''
        raise NotImplementedError(
            'subclass of AbstractMergerDialog need a '
            'create_buttons(self) reimplemented')
        return [QtGui.QPushButton()]

    def _create_filters_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        for filters_widget in self._filters_widgets:
            layout.addWidget(filters_widget)
        layout.addStretch(1)
        return layout

    def _create_buttons_layout(self):
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        for button in self._buttons:
            layout.addWidget(button)
        return layout

    def create_filters_view(self, caption, method, datas=[]):
        filters_view = FitlersView(caption, datas)
        filters_view.filtersChanged.connect(method)
        filters_view.isOpened.connect(partial(self.close_tabs, filters_view))
        return filters_view

    def close_tabs(self, widget):
        for filters_widget in self._filters_widgets:
            if filters_widget != widget:
                filters_widget.close_tab()

    def set_datas(self, datas):
        self.datas = datas
        self._list_model.set_datas(self.datas)
        self._list_view.refresh()

    def on_list_model_edited(self, state):
        indexes = self._list_view.get_selected_indexes()
        self._list_model.set_checked_indexes(indexes, state)
        self._list_view.set_selected_indexes(indexes)


class PrintablesMerger(AbstractMergerDialog):

    def create_filters(self):
        bands = [band.name for band in PizzicatoController.context.bands]
        self._filters_view_bands = self.create_filters_view(
            text.BANDS, self.on_filters_view_bands_filters_changed, datas=bands)

        self._filters_view_pieces = self.create_filters_view(
            text.PIECES, self._update_printables_files)

        self._filters_view_instruments = self.create_filters_view(
            text.INSTRUMENTS, self._update_printables_files)

        return [
            self._filters_view_bands,
            self._filters_view_pieces,
            self._filters_view_instruments]

    def create_list_model(self):
        model = PrintableTableModel()
        model.edited.connect(self.on_list_model_edited)
        return model

    def create_buttons(self):
        merge = QtGui.QPushButton(text.MERGE)
        merge.clicked.connect(self.on_merge_clicked)
        cancel = QtGui.QPushButton(text.CANCEL)
        cancel.clicked.connect(self.close)
        return [merge, cancel]

    def on_filters_view_bands_filters_changed(self):
        pieces = []
        instruments = []
        for band in PizzicatoController.context.bands:
            if band.name in self._filters_view_bands.filters:
                pieces += [piece.title for piece in band.pieces]
                instruments += band.instruments
        instruments = list(set(instruments))
        self._filters_view_pieces.set_datas(pieces)
        self._filters_view_instruments.set_datas(instruments)
        self._update_printables_files()

    def on_merge_clicked(self):
        dst = QtGui.QFileDialog.getSaveFileName(
            parent=self, caption=text.FILE_DIALOG_SAVE_PDF_FILES,
            directory='', filter='*.pdf')
        files = self._list_model.get_selected_datas()
        PizzicatoController.merge_pdf_file(files, dst)
        return self.close()

    def _update_printables_files(self):
        self._files = [
            f for f in PizzicatoController.context.printables
            if f.piece.name in self._filters_view_pieces.filters and
            f.instrument in self._filters_view_instruments.filters]
        self._list_model.set_datas(self._files)
        self._list_view.refresh()


class AudioZipper(AbstractMergerDialog):

    def create_filters(self):
        #  band filter
        bands = [band.name for band in PizzicatoController.context.bands]
        self._filters_view_bands = self.create_filters_view(
            text.BANDS, self.on_filters_view_bands_filters_changed, datas=bands)

        #  pieces filter
        self._filters_view_pieces = self.create_filters_view(
            text.PIECES, self._update_audios_files)

        #  extentions filter
        extentions_descriptions = [
            extention.extention_description
            for extention in PizzicatoPreferences.AUDIOS_SUPPORTED_EXTENSIONS]
        self._filters_view_extentions = self.create_filters_view(
            text.EXTENTION_AUDIOS, self._update_audios_files,
            datas=extentions_descriptions)

        #  extentions filter
        categories = ([
            PizzicatoEnums.MUSIC_FILE_CATEGORIES[key]
            for key in PizzicatoEnums.MUSIC_FILE_CATEGORIES] +
            [PizzicatoEnums.MUSIC_FILE_CATEGORIE_UNDEFINED])
        self._filters_view_categories = self.create_filters_view(
            text.CATEGORIES, self._update_audios_files,
            datas=categories)

        return [
            self._filters_view_bands,
            self._filters_view_pieces,
            self._filters_view_extentions,
            self._filters_view_categories]

    def create_list_model(self):
        model = AudiosTableModel()
        model.edited.connect(self.on_list_model_edited)
        return model

    def create_buttons(self):
        zip = QtGui.QPushButton(text.ZIP)
        zip.clicked.connect(self.on_zip_clicked)
        cancel = QtGui.QPushButton(text.CANCEL)
        cancel.clicked.connect(self.close)
        return [zip, cancel]

    def on_filters_view_bands_filters_changed(self):
        pieces = []
        extention = []
        for band in PizzicatoController.context.bands:
            if band.name in self._filters_view_bands.filters:
                pieces += [piece.title for piece in band.pieces]
        self._filters_view_pieces.set_datas(pieces)
        self._update_audios_files()

    def on_zip_clicked(self):
        dst = QtGui.QFileDialog.getSaveFileName(
            parent=self, caption=text.FILE_DIALOG_SAVE_ZIP_FILES,
            directory='', filter='*.zip')
        files = self._list_model.get_selected_datas()
        PizzicatoController.zip_audio_files(files, dst)
        return self.close()

    def _update_audios_files(self):
        self._files = [
            f for f in PizzicatoController.context.audios
            if f.piece.name in self._filters_view_pieces.filters and
            f.extention.extention_description
            in self._filters_view_extentions.filters and
            f.categorie in self._filters_view_categories.filters]
        self._list_model.set_datas(self._files)
        self._list_view.refresh()


############################
#### Merger Table Model ####
############################


class MergerAbstractTableModel(QtCore.QAbstractTableModel):
    edited = QtCore.pyqtSignal(bool)
    headers = ['']

    def __init__(self, datas=[], parent=None):
        super(MergerAbstractTableModel, self).__init__(parent)
        self._datas = [[QtCore.Qt.Checked, data] for data in datas]
        self._parent = parent

    def rowCount(self, index=None):
        return len(self._datas)

    def columnCount(self, index=None):
        return len(self.headers)

    def set_datas(self, datas):
        self.clear()
        if not isinstance(datas, list):
            datas = [datas]
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(datas) - 1)
        self._datas = [[QtCore.Qt.Checked, data] for data in datas]
        self.endInsertRows()

    def set_checked_indexes(self, indexes, state):
        state = QtCore.Qt.Checked if state else QtCore.Qt.Unchecked
        for index in indexes:
            if not isinstance(index, int):
                index = index.row()
            self._datas[index][0] = state
        self.dataChanged.emit(
            self.index(0, 0, QtCore.QModelIndex()),
            self.index(self.rowCount(), 0, QtCore.QModelIndex()))

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self.headers[section]

    def flags(self, index):
        flags = super(MergerAbstractTableModel, self).flags(index)
        if index.column() == 0:
            return flags | QtCore.Qt.ItemIsUserCheckable
        else:
            return flags

    def clear(self):
        return self.reset()

    def setData(self, index=None, value=None, role=QtCore.Qt.EditRole):
        row = index.row()
        if role == QtCore.Qt.CheckStateRole:
            self.edited.emit(value == QtCore.Qt.Checked)
            self._datas[row][0] = value
        return True

    def get_selected_datas(self):
        return [data[1] for data in self._datas if data[0]]

    def data(self, index, role):
        '''
        Have to reimplant this methods in sub classes
                '''
        raise NotImplementedError(
            'subclass of MergerAbstractTableModel need a '
            'data((self, index, role) reimplemented method')


class PrintableTableModel(MergerAbstractTableModel):
    headers = ('', text.INSTRUMENT,  text.PIECE, text.BAND)

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return str()
            if col == 1:
                return self._datas[row][1].title
            elif col == 2:
                return self._datas[row][1].instrument
            elif col == 3:
                return self._datas[row][1].piece.band.name
        if role == QtCore.Qt.CheckStateRole:
            if col == 0:
                return self._datas[row][0]
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft

    def sort(self, column, order):
        if column == 0:
            return
        self.layoutAboutToBeChanged.emit()
        if column == 1:
            self._datas = sorted(
                self._datas, key=lambda data: data[1].title)
        if column == 2:
            self._datas = sorted(
                self._datas, key=lambda data: data[1].instrument)
        if column == 3:
            self._datas = sorted(
                self._datas, key=lambda data: data[1].piece.band.name)
        if order == QtCore.Qt.DescendingOrder:
            self._datas.reverse()
        self.layoutChanged.emit()


class AudiosTableModel(MergerAbstractTableModel):
    headers = (
        '', text.TITLE,  text.PIECE, text.EXTENTION, text.CATEGORIE)

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return str()
            if col == 1:
                return self._datas[row][1].name
            elif col == 2:
                return self._datas[row][1].extention.extention_description
            elif col == 3:
                return self._datas[row][1].piece.band.name
            elif col == 4:
                return self._datas[row][1].categorie
        if role == QtCore.Qt.CheckStateRole:
            if col == 0:
                return self._datas[row][0]
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()

        if column == 0:
            return
        elif column == 1:
            self._datas = sorted(
                self._datas, key=lambda data: data[1].name)
        elif column == 2:
            self._datas = sorted(
                self._datas, key=lambda data: data[1].extention.extention_description)
        elif column == 3:
            self._datas = sorted(
                self._datas, key=lambda data: data[1].piece.band.name)
        elif column == 4:
            self._datas = sorted(
                self._datas, key=lambda data: data[1].categorie)

        if order == QtCore.Qt.DescendingOrder:
            self._datas.reverse()

        self.layoutChanged.emit()


class MergerListView(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MergerListView, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self._table_view = self._create_table_view()

        self._check_all = QtGui.QPushButton(text.SELECT_ALL)
        self._check_all.clicked.connect(
            partial(self.on_check, QtCore.Qt.Checked))
        self._check_none = QtGui.QPushButton(text.SELECT_NONE)
        self._check_none.clicked.connect(
            partial(self.on_check, QtCore.Qt.Unchecked))

        self._buttons_h_layout = QtGui.QHBoxLayout()
        self._buttons_h_layout.addWidget(self._check_all)
        self._buttons_h_layout.addWidget(self._check_none)

        self._layout = QtGui.QVBoxLayout(self)
        self._layout.addWidget(self._table_view)
        self._layout.addLayout(self._buttons_h_layout)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def _create_table_view(self):
        table = QtGui.QTableView()
        table.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        table.verticalHeader().hide()
        table.horizontalHeader().hide()
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.setDragEnabled(True)
        table.setDropIndicatorShown(True)
        table.setShowGrid(False)
        table.setWordWrap(False)
        table.setSortingEnabled(True)
        table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        return table

    def get_selected_indexes(self):
        selection_model = self._table_view.selectionModel()
        return selection_model.selectedIndexes()

    def set_selected_indexes(self, indexes):
        selection_model = self._table_view.selectionModel()
        model = self._table_view.model()
        for index in indexes:
            index = model.index(index.row(), 0, QtCore.QModelIndex())
            selection_model.select(index, QtGui.QItemSelectionModel.Select)

    def setModel(self, model):
        self._table_view.setModel(model)
        self.refresh()

    def on_check(self, state):
        model = self._table_view.model()
        model.set_checked_indexes(range(model.rowCount()), state)
        self._table_view.update()

    def refresh(self):
        model = self._table_view.model()
        if model.rowCount():
            self._table_view.horizontalHeader().resizeSections(
                QtGui.QHeaderView.ResizeToContents)
            self._table_view.horizontalHeader().show()
            self._table_view.horizontalHeader().setStretchLastSection(True)
        else:
            self._table_view.horizontalHeader().hide()
