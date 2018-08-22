from Pizzicato.controllers import PizzicatoController
from Pizzicato.functions import get_index_for_insertion_in_sorted_list
from Pizzicato.extentions import FilesExtention
from Pizzicato import text

from PyQt5 import QtGui, QtCore, QtWidgets
import os


class BandsTableModel(QtCore.QAbstractTableModel):

    def __init__(self, datas, is_list=True, parent=None):
        super(BandsTableModel, self).__init__(parent=parent)
        PizzicatoController.append_bands_models(self)
        print(datas)
        self._datas = datas
        self._is_list = is_list

    def rowCount(self, _):
        return len(self._datas)

    def columnCount(self, _):
        return 2

    def get_band(self, index):
        if len(self._datas):
            return self._datas[index]

    def get_band_index(self, band):
        return self._datas.index(band)

    def add_band(self, band):
        index = get_index_for_insertion_in_sorted_list(self._datas, band)
        self.beginInsertRows(QtCore.QModelIndex(), index, index + 1)
        self._datas.insert(index, band)
        self.endInsertRows()

    def remove_band(self, band):
        index = self._datas.index(band)
        self.beginRemoveRows(QtCore.QModelIndex(), index, index + 1)
        self._datas.remove(band)
        self.endRemoveRows()

    def data(self, index, role):
        row, col = index.row(), index.column()

        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                if self._is_list:
                    return (
                        self._datas[row].name +
                        u'  (contain {} piece(s))'.format(
                            self._datas[row].piece_number))
                else:
                    return self._datas[row].name
            if col == 1:
                return u'(contain {} piece(s))'.format(
                    self._datas[row].piece_number)

        if role == QtCore.Qt.TextColorRole:
            if col == 1:
                return QtGui.QColor(125, 125, 125)

        if role == QtCore.Qt.FontRole:
            if col == 1:
                font = QtGui.QFont()
                font.italic(True)
                return font


class BandsTableView(QtWidgets.QTableView):

    def __init__(self, model, parent=None):
        super(BandsTableView, self).__init__(parent)
        self._model = model
        self.initUI()

    def initUI(self):
        self._configure()
        self.setModel(self._model)

    def _configure(self):
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.setWordWrap(True)


class BandsComboBoxView(QtWidgets.QComboBox):

    def __init__(self, model, parent=None):
        super(BandsComboBoxView, self).__init__(parent)
        self._model = model
        self.initUI()

    def initUI(self):
        self._configure()
        self.setModel(self._model)

    def _configure(self):
        PizzicatoController.bands_combo_view = self
        self.setEditable(False)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    def get_current_band(self):
        return self._model.get_band(self.currentIndex())

    def select_band(self, band):
        index = self._model.get_band_index(band)
        self.setCurrentIndex(index)


class PieceListModel(QtCore.QAbstractListModel):
    edited = QtCore.pyqtSignal()

    def __init__(self, checkable=False, parent=None):
        super(PieceListModel, self).__init__(parent=parent)
        PizzicatoController.append_pieces_models(self)
        self._checkable = checkable
        self._pieces = None

    def set_bands(self, bands):
        self.layoutAboutToBeChanged.emit()
        if not isinstance(bands, list):
            bands = [bands]
        self._pieces = []
        for band in bands:
            self._pieces += band.pieces
        self.layoutChanged.emit()

    def rowCount(self, _):
        if self._pieces is None:
            return 0
        return len(self._pieces)

    def add_piece(self, piece):
        index = get_index_for_insertion_in_sorted_list(self._pieces, piece)
        self.beginInsertRows(QtCore.QModelIndex(), index, index + 1)
        self._pieces.insert(index, piece)
        self.endInsertRows()

    def remove_piece(self, piece):
        index = self._pieces.index(piece)
        self.beginRemoveRows(QtCore.QModelIndex(), index, index + 1)
        self._pieces.remove(piece)
        self.endRemoveRows()

    def get_piece(self, index):
        return self._pieces[index]

    def data(self, index, role):
        if not index.isValid():
            return False
        row = index.row()

        if role == QtCore.Qt.DisplayRole:
            return self._pieces[row].title

        if role == QtCore.Qt.EditRole:
            return self._pieces[row].title

        if self._checkable:
            if role == QtCore.Qt.CheckStateRole:
                return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(
            QtCore.QAbstractListModel.flags(self, index) |
            QtCore.Qt.ItemIsEditable)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        if not index.isValid():
            return False
        if role == QtCore.Qt.EditRole:
            self._pieces[row].rename(value)
            self.edited.emit()

        return True


class PieceListView(QtWidgets.QListView):

    def __init__(self, model, parent=None):
        super(PieceListView, self).__init__(parent)
        self._model = model
        self.initUI()

    def initUI(self):
        self._configure()
        self.setModel(self._model)

    def _configure(self):
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)


class FilesAbstractTableModel(QtCore.QAbstractTableModel):

    def __init__(self, columns=[], parent=None):
        super(FilesAbstractTableModel, self).__init__(parent)
        self._datas = None
        self._columns = columns

    def rowCount(self, _):
        if self._datas is None:
            return 0
        return len(self._datas)

    def columnCount(self, _):
        return len(self._columns)

    def clear(self):
        return self.resetInternalData()

    def get_data(self, index):
        return self._datas[index]

    def set_datas(self, datas):
        self.clear()
        if not isinstance(datas, list):
            datas = [datas]
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(datas) - 1)
        self._datas = datas
        self.endInsertRows()

    def add_file(self, file):
        self.beginInsertRows(
            QtCore.QModelIndex(), len(self._datas), len(self._datas) + 1)
        self._datas.append(file)
        self.endInsertRows()

    def headerData(self, index, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._columns[index][0]

    def data(self, index, role):
        row, col = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole:
            return self._datas[row].__getattribute__(self._columns[col][1])

        if role == QtCore.Qt.BackgroundColorRole:
            if not row % 2 == 0:
                return QtGui.QColor(0, 0, 0, 20)

        if role == QtCore.Qt.ToolTipRole:
            return self._datas[row].path


class AudioFilesTableModel(FilesAbstractTableModel):

    def __init__(self, columns=[], parent=None):
        super(AudioFilesTableModel, self).__init__(parent)
        self._datas = None
        self._columns = columns

    def flags(self, index):
        if index.column() == 1:
            return QtCore.Qt.ItemFlags(
                super().flags(index) |
                QtCore.Qt.ItemIsEditable)
        else:
            return super(AudioFilesTableModel, self).flags(index)

    def setData(self, index, value, _):
        audio_file = self._datas[index.row()]
        PizzicatoController.rename_audio_file(audio_file, value)
        return True

    def data(self, index, role):
        if role == QtCore.Qt.EditRole:
            row, col = index.row(), index.column()
            return self._datas[row].__getattribute__(self._columns[col][1])
        else:
            return FilesAbstractTableModel.data(self, index, role)


class FilesTableView(QtWidgets.QTableView):
    selectionIsChanged = QtCore.pyqtSignal()
    droppedFiles = QtCore.pyqtSignal(list)

    def __init__(self, model=FilesAbstractTableModel(), parent=None, menu=None):
        super(FilesTableView, self).__init__(parent)
        self._model = model
        self._menu = menu
        self._filters = None
        self.initUI()

    def initUI(self):
        self.configure()
        self.setModel(self._model)
        self._selection_model = self.selectionModel()
        self._selection_model.selectionChanged.connect(
            self.selectionIsChanged.emit)
        self.customContextMenuRequested.connect(self.on_context_menu_requested)

    def configure(self):
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setDragDropOverwriteMode(True)

    def set_filters(self, extentions):
        self._filters = extentions

    def get_selected_data(self):
        indexes = self._selection_model.selectedIndexes()
        if not len(indexes):
            return None

        index = indexes[0].row()
        return self._model.get_data(index)

    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls() or self._filters is None:
            return event.reject()

        urls = event.mimeData().urls()
        valid = any(
            [self._filters.is_url_extention_in_list(url) for url in urls])
        if valid:
            return event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        dropped_urls = event.mimeData().urls()
        valid_urls = []
        for url in dropped_urls:
            if self._filters.is_url_extention_in_list(url):
                valid_urls.append(url)
        urls = []
        for url in valid_urls:
            urls.append(os.path.normpath(url.path()[1:]))
        self.droppedFiles.emit(urls)

    def on_context_menu_requested(self, point):
        selected_file = self.get_selected_data()
        if not selected_file or not self._menu:
            return

        self._menu.set_abstract_file(selected_file)
        self._menu.exec_(self.mapToGlobal(point))


class WipFilesTableView(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(WipFilesTableView, self).__init__(parent)
        self._root = '/'

        self._tree_view = QtWidgets.QTreeView(self)
        self._file_system_model = QtWidgets.QFileSystemModel(self._tree_view)
        self._file_system_model.setReadOnly(True)

        self._tree_view.setModel(self._file_system_model)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._tree_view)

    def set_root_path(self, path):
        root = self._file_system_model.setRootPath(path)
        self._tree_view.setRootIndex(root)


class ExtentionsTableView(QtWidgets.QTableView):
    dataSelected = QtCore.pyqtSignal(FilesExtention)

    def __init__(self, parent=None):
        super(ExtentionsTableView, self).__init__(parent)
        self.initUI()
        self.configure()

    def initUI(self):
        self._model = None
        self._selection_model = None

    def configure(self):
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setDragDropOverwriteMode(True)

    def setModel(self, model):
        super(ExtentionsTableView, self).setModel(model)
        self._model = model
        self._selection_model = self.selectionModel()
        self._selection_model.selectionChanged.connect(
            self.on_selection_model_selectionChanged)

    def on_selection_model_selectionChanged(self, indexes):
        if len(indexes):
            row = indexes[0].indexes()[0].row()
            self.dataSelected.emit(self._model.get_data(row))


class ExtentionsTableModel(QtCore.QAbstractTableModel):
    headers = (text.EXTENTION, text.DESCRIPTION, text.PROGRAM, text.PATH)

    def __init__(self, datas=[], parent=None):
        super(ExtentionsTableModel, self).__init__(parent)
        self._datas = datas

    def rowCount(self, _):
        if self._datas is None:
            return 0
        return len(self._datas)

    def columnCount(self, _):
        return 4

    def headerData(self, index, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.headers[index]

    def get_data(self, index):
        return self._datas[index]

    def set_datas(self, datas):
        self.clear()
        if not isinstance(datas, list):
            datas = [datas]
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(datas) - 1)
        self._datas = datas
        self.endInsertRows()

    def clear(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self._datas) - 1)
        self._datas = []
        self.endRemoveRows()

    def data(self, index, role):
        if not index.isValid():
            return False
        row, col = index.row(), index.column()

        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return self._datas[row].extention
            if col == 1:
                return self._datas[row].extention_description
            if col == 2:
                return self._datas[row].program
            if col == 3:
                return self._datas[row].bin_path
