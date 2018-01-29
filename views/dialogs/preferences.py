from PyQt4 import QtGui, QtCore
from Pizzicato.preferences import PizzicatoPreferences
from Pizzicato.controllers import PizzicatoPreferencesController
from Pizzicato.views.tables import ExtentionsTableModel, ExtentionsTableView
from Pizzicato.views.utils import EditLineWithPathSelector
from Pizzicato.extentions import FilesExtention
from Pizzicato import text


class PreferencesEditor(QtGui.QWidget):

    def __init__(self, parent=None):
        super(PreferencesEditor, self).__init__(parent, QtCore.Qt.Window)
        self._visible_widget_index = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle(text.DIALOG_PREFERENCES)

        self._settable_widget = self._create_settable_widget()
        self._settable_widgets = self._create_settable_widgets()

        self._list = self._create_list()
        self._buttons_layout = self._create_buttons_layout()

        self._layout_right = self._create_layout_right()
        self._layout = QtGui.QHBoxLayout(self)
        self._layout.addWidget(self._list)
        self._layout.addLayout(self._layout_right)

        self.update_visible_widget()

    def _create_settable_widget(self):
        widget = QtGui.QWidget()
        widget.resize(300, 600)
        widget.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        return widget

    def _create_settable_widgets(self):
        widgets = (
            GeneralPreferences(),
            self._create_extention_preferences())
        layout = QtGui.QHBoxLayout(self._settable_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            layout.addWidget(widget)
        return widgets

    def _create_layout_right(self):
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._settable_widget)
        layout.addLayout(self._buttons_layout)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def _create_list(self):
        widget = QtGui.QListWidget()
        widget.addItems(['General', 'Extentions'])
        item = widget.item(0)
        widget.setItemSelected(item, True)
        widget.setSizePolicy(
            QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        widget.itemSelectionChanged.connect(self.update_visible_widget)
        return widget

    def _create_buttons_layout(self):
        ok = QtGui.QPushButton(text.OK)
        ok.clicked.connect(self.on_ok_clicked)
        cancel = QtGui.QPushButton(text.CANCEL)
        cancel.clicked.connect(self.close)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        layout.addWidget(ok)
        layout.addWidget(cancel)
        return layout

    def _create_extention_preferences(self):
        widget = ExtentionsPreferences(self._settable_widget)
        widget.set_extentions_type({
            text.EXTENTION_AUDIOS: PizzicatoPreferences.AUDIOS_SUPPORTED_EXTENSIONS,
            text.EXTENTION_EDITABLES: PizzicatoPreferences.EDITABLES_SUPPORTED_EXTENSIONS,
            text.EXTENTION_PRINTABLES: PizzicatoPreferences.PRINTABLES_SUPPORTED_EXTENSIONS})
        return widget

    def update_visible_widget(self):
        index = self._list.currentIndex().row()
        index = 0 if index not in range(self._list.count()) else index
        self._visible_widget_index = index
        for i, widget in enumerate(self._settable_widgets):
            if i == index:
                widget.show()
            else:
                widget.hide()
        self._visible_widget_index = index

    def on_ok_clicked(self):
        values = self._settable_widgets[0].get_values()
        PizzicatoPreferencesController.set_values(
            PizzicatoPreferences, values)
        self.close()


class GeneralPreferences(QtGui.QWidget):

    def __init__(self, parent=None):
        super(GeneralPreferences, self).__init__(parent)
        self.configure()
        self.initUI()

    def configure(self):
        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

    def initUI(self):
        self._layout = QtGui.QGridLayout(self)

        self._languages_selector = self._create_languages_selector()
        self._paths_editor = self._create_paths_editor()

        self._layout.addWidget(QtGui.QLabel(text.PREF_LANGUAGE_SELECT), 0, 0)
        self._layout.addWidget(self._languages_selector, 0, 1)
        self._layout.addWidget(self._paths_editor, 1, 0, 1, 2)
        self._layout.setRowStretch(2, 1)

    def _create_languages_selector(self):
        combo = QtGui.QComboBox()
        combo.setSizePolicy(*[QtGui.QSizePolicy.Expanding] * 2)
        combo.addItems(PizzicatoPreferences.LANGUAGES_AVAILABLES)
        combo.setCurrentIndex(PizzicatoPreferences.LANGUAGES_INDEX)
        return combo

    def _create_paths_editor(self):
        widget = QtGui.QGroupBox(text.PREF_PATH_EDITOR)
        layout = QtGui.QFormLayout(widget)

        self._finals = QtGui.QLineEdit(PizzicatoPreferences.FINALS_FOLDER)
        self._wip = QtGui.QLineEdit(PizzicatoPreferences.WIP_FOLDER)

        self._audios = QtGui.QLineEdit(PizzicatoPreferences.AUDIOS_FOLDER)
        self._printables = QtGui.QLineEdit(
            PizzicatoPreferences.PRINTABLES_FOLDER)
        self._editables = QtGui.QLineEdit(
            PizzicatoPreferences.EDITABLES_FOLDER)

        self._piece_properties = QtGui.QLineEdit(
            PizzicatoPreferences.PIECE_PROPERTIES_FILENAME)

        layout.addRow(text.PREF_PATH_EDITOR_FINALS + ' :', self._finals)
        layout.addRow(text.PREF_PATH_EDITOR_WIP + ' :', self._wip)
        layout.addRow(text.PREF_PATH_EDITOR_AUDIOS + ' :', self._audios)
        layout.addRow(
            text.PREF_PATH_EDITOR_PRINTABLES + ' :', self._printables)
        layout.addRow(text.PREF_PATH_EDITOR_EDITABLES + ' :', self._editables)
        layout.addRow(
            text.PREF_PATH_EDITOR_PROPERTIES + ' :', self._piece_properties)

        return widget

    def get_values(self):
        return {
            'LANGUAGES_INDEX': self._languages_selector.currentIndex(),
            'AUDIOS_FOLDER': self._audios.text(),
            'PRINTABLES_FOLDER': self._printables.text(),
            'EDITABLES_FOLDER': self._editables.text(),
            'FINALS_FOLDER': self._finals.text(),
            'WIP_FOLDER': self._wip.text(),
            'PIECE_PROPERTIES_FILENAME': self._piece_properties.text()
        }


class ExtentionsPreferences(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ExtentionsPreferences, self).__init__(parent)
        self.configure()
        self.initUI()

    def configure(self):
        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

    def initUI(self):
        self._extention_editor = ExtentionEditor()
        self._extentions_selector = ExtentionsSelector()

        self._layout = QtGui.QVBoxLayout(self)
        self._layout.addWidget(self._extentions_selector)
        self._layout.addWidget(self._extention_editor)
        self._layout.addStretch(1)

        self._extentions_selector.extentionSelected.connect(
            self._extention_editor.set_extention)

    def set_extentions_type(self, dict_of_extentions_list):
        self._extentions_selector.set_extentions_type(dict_of_extentions_list)


class ExtentionsSelector(QtGui.QWidget):
    extentionSelected = QtCore.pyqtSignal(FilesExtention)

    def __init__(self, parent=None):
        super(ExtentionsSelector, self).__init__(parent)
        self._lists = []
        self.initUI()

    def initUI(self):
        self._layout = QtGui.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._combo_selector = self._create_combo_selector()
        self._extention_table_model = ExtentionsTableModel()
        self._extention_table_view = ExtentionsTableView()
        self._extention_table_view.setModel(self._extention_table_model)
        self._extention_table_view.dataSelected.connect(
            self.extentionSelected.emit)

        self._layout.addWidget(self._combo_selector)
        self._layout.addWidget(self._extention_table_view)

    def _create_combo_selector(self):
        widget = QtGui.QWidget()
        widget.label = QtGui.QLabel(text.EXTENTION_TYPE_SELECT + ' :')

        widget.combo = QtGui.QComboBox()
        widget.combo.currentIndexChanged.connect(self._set_extentions_list)
        widget.combo.setSizePolicy(*[QtGui.QSizePolicy.Expanding] * 2)
        widget.clear = widget.combo.clear
        widget.addItem = widget.combo.addItem

        layout = QtGui.QHBoxLayout(widget)
        layout.addWidget(widget.label)
        layout.addWidget(widget.combo)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget

    def _set_extentions_list(self, index):
        self._extention_table_model.set_datas(self._lists[index])

    def set_extentions_type(self, dict_of_extentions_list):
        self._combo_selector.clear()
        for key in sorted(dict_of_extentions_list.keys()):
            self._combo_selector.addItem(key)
            self._lists.append(dict_of_extentions_list[key])
        self._set_extentions_list(0)


class ExtentionEditor(QtGui.QGroupBox):

    def __init__(self, parent=None):
        super(ExtentionEditor, self).__init__(parent)
        self._extention = None
        self.configure()
        self.initUI()

    def configure(self):
        self.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

    def initUI(self):
        self.setTitle(text.EXTENTION_EDIT)
        self._layout = QtGui.QFormLayout(self)

        self._edit_extention = QtGui.QLineEdit()
        self._edit_extention_full_name = QtGui.QLineEdit()
        self._edit_program = QtGui.QLineEdit()
        self._edit_bin_path = EditLineWithPathSelector()

        self._layout.addRow(text.EXTENTION + ' :', self._edit_extention)
        self._layout.addRow(
            text.DESCRIPTION + ' :', self._edit_extention_full_name)
        self._layout.addRow(text.PROGRAM + ' :', self._edit_program)
        self._layout.addRow(text.BIN_PATH + ' :', self._edit_bin_path)

    def set_extention(self, extention):
        self._extention = extention
        self._update_texts()

    def _update_texts(self):
        self._edit_extention.setText(self._extention.extention)
        self._edit_extention_full_name.setText(
            self._extention.extention_description)
        self._edit_program.setText(self._extention.program)
        self._edit_bin_path.set_text(self._extention.bin_path)
