# from PyQt5.phonon import Phonon
from PyQt5 import QtCore, QtWidgets
from Pizzicato import text
from functools import partial
import os


def warning(message, question=False, title='Warning !'):
    if not question:
        return QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning, title, message, buttons=QtWidgets.QMessageBox.Ok)
    else:
        question = QtWidgets.QMessageBox.warning(
            None, title, message, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)
        return True if question == QtWidgets.QMessageBox.AcceptRole else False


class LineEditAsLabel(QtWidgets.QLineEdit):

    def __init__(self, caption, parent=None):
        super(LineEditAsLabel, self).__init__(caption, parent)


class FloatEditLineWidget(QtWidgets.QLineEdit):
    accepted = QtCore.pyqtSignal()
    rejected = QtCore.pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            return self.accepted.emit()

        if event.key() == QtCore.Qt.Key_Escape:
            return self.rejected.emit()

        super(FloatEditLineWidget, self).keyPressEvent(event)

    def focusOutEvent(self, _):
        return self.rejected.emit()


class FloatEditLineView(QtWidgets.QWidget):
    accepted = QtCore.pyqtSignal(str)

    def __init__(self, caption, parent=None):
        super(FloatEditLineView, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._caption = caption
        self.initUI()

    def initUI(self):
        self._float_edit_line_widget = FloatEditLineWidget(self._caption)
        self._float_edit_line_widget.setFocus()
        self._float_edit_line_widget.selectAll()
        self._float_edit_line_widget.accepted.connect(self.accept)
        self._float_edit_line_widget.rejected.connect(self.close)

        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._float_edit_line_widget)

    def accept(self):
        self.accepted.emit(self._float_edit_line_widget.text())
        self.close()


# class SoundReader(QtWidgets.QWidget):

#     def __init__(self, parent=None):
#         super(SoundReader, self).__init__(parent)
#         self._audio_file = None
#         self._media_object = Phonon.MediaObject(self)
#         self._audio_output = Phonon.AudioOutput(Phonon.MusicCategory, self)

#         self._media_object.setTickInterval(1000)
#         self._media_object.tick.connect(
#             self.on_media_object_tick)
#         self._media_object.stateChanged.connect(
#             self.on_media_object_stateChanged)
#         self._media_object.aboutToFinish.connect(
#             self._media_object.stop)

#         Phonon.createPath(self._media_object, self._audio_output)
#         self.initUI()

#     def initUI(self):
#         self._actions = self._create_actions()
#         self._actions_bar = self._create_actions_bar()
#         self._seek_slider = Phonon.SeekSlider(self)
#         self._seek_slider.setMediaObject(self._media_object)
#         self._time = QtWidgets.QLabel('00:00')
#         self._volume_slider = Phonon.VolumeSlider(self)
#         self._volume_slider.setAudioOutput(self._audio_output)

#         self._layout = QtWidgets.QHBoxLayout(self)
#         self._layout.setContentsMargins(0, 0, 0, 0)
#         self._layout.addWidget(self._actions_bar)
#         self._layout.addWidget(self._seek_slider)
#         self._layout.addWidget(self._time)
#         self._layout.addWidget(self._volume_slider)

#     def _create_actions(self):
#         style = self.style()
#         actions = QtWidgets.QWidget(self)

#         actions.play = QtWidgets.QAction(
#             style.standardIcon(QtWidgets.QStyle.SP_MediaPlay), '', self)
#         actions.play.triggered.connect(self.on_play)
#         actions.play.setEnabled(False)

#         actions.pause = QtWidgets.QAction(
#             style.standardIcon(QtWidgets.QStyle.SP_MediaPause), '', self)
#         actions.pause.triggered.connect(self._media_object.pause)
#         actions.pause.setEnabled(False)

#         actions.stop = QtWidgets.QAction(
#             style.standardIcon(QtWidgets.QStyle.SP_MediaStop), '', self)
#         actions.stop.triggered.connect(self._media_object.stop)
#         actions.stop.setEnabled(False)

#         return actions

#     def _create_actions_bar(self):
#         widget = QtWidgets.QMenuBar(self)
#         widget.addAction(self._actions.play)
#         widget.addAction(self._actions.pause)
#         widget.addAction(self._actions.stop)
#         return widget

#     def on_media_object_tick(self, time):
#         time = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
#         self._time.setText(time.toString('mm:ss'))

#     def set_music_file(self, audio_file):
#         self._audio_file = audio_file
#         if os.path.exists(self._audio_file.path):
#             self._actions.play.setEnabled(True)

#     def on_play(self):
#         current_source_path = os.path.normpath(
#             self._media_object.currentSource().fileName())
#         if current_source_path == self._audio_file.path:
#             self._media_object.play()
#         else:
#             self._media_object.setCurrentSource(
#                 Phonon.MediaSource(self._audio_file.path))
#             self._media_object.play()
#         self._actions.stop.setEnabled(True)
#         self._actions.pause.setEnabled(True)

#     def on_media_object_stateChanged(self, new_state, _):
#         if new_state == Phonon.ErrorState:
#             if self._media_object.errorType() == Phonon.FatalError:
#                 QtWidgets.QMessageBox.warning(self, self.tr("Fatal Error"),
#                                           self.mediaObject.errorString())
#             else:
#                 QtWidgets.QMessageBox.warning(self, self.tr("Error"),
#                                           self.mediaObject.errorString())

#         elif new_state == Phonon.PlayingState:
#             self._actions.play.setEnabled(False)
#             self._actions.pause.setEnabled(True)
#             self._actions.stop.setEnabled(True)

#         elif new_state == Phonon.StoppedState:
#             self._actions.play.setEnabled(True)
#             self._actions.pause.setEnabled(False)
#             self._actions.stop.setEnabled(False)
#             self._time.setText("00:00")

#         elif new_state == Phonon.PausedState:
#             self._actions.play.setEnabled(True)
#             self._actions.pause.setEnabled(False)
#             self._actions.stop.setEnabled(True)


class PrintablesImportFileView(QtWidgets.QGroupBox):

    def __init__(self, path, parent=None):
        super(PrintablesImportFileView, self).__init__(parent)
        self._file = path
        self.configure()
        self.initUI()

    def configure(self):
        self.setTitle(os.path.basename(self._file))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def initUI(self):
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self._combobox = self._create_combobox()
        self._combobox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self._closer = self._create_closer()

        self._layout.addWidget(self._combobox)
        self._layout.addWidget(self._closer)

    def _create_combobox(self):
        combo = QtWidgets.QComboBox()
        combo.setEditable(True)
        return combo

    def _create_closer(self):
        style = self.style()
        button = QtWidgets.QPushButton(
            style.standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton), '')
        button.setFixedSize(20, 20)
        button.clicked.connect(self.close)
        return button

    def fill_combobox_and_set_text(self, strings, text):
        index = [i for i, t in enumerate(strings) if text == t][0]
        self._combobox.addItems(strings)
        self._combobox.setCurrentIndex(index)

    def instrument(self):
        return self._combobox.currentText()

    def path(self):
        return self._file


class EditLineWithPathSelector(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(EditLineWithPathSelector, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._path = QtWidgets.QLineEdit()
        self._path.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self._open = self._create_open()

        self._layout.addWidget(self._path)
        self._layout.addWidget(self._open)

    def _create_open(self):
        style = self.style()
        open = QtWidgets.QPushButton(style.standardIcon(style.SP_DirOpenIcon), '')
        open.setFixedSize(22, 22)
        open.clicked.connect(self.on_open_clicked)
        return open

    def on_open_clicked(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            parent=self, caption='pick a program', directory='c:', filter='*.exe')
        return self.set_text(path)

    def set_text(self, text):
        self._path.setText(text)


class FitlersView(QtWidgets.QWidget):
    filtersChanged = QtCore.pyqtSignal(list)
    isOpened = QtCore.pyqtSignal()

    def __init__(self, caption, datas=[], parent=None):
        super(FitlersView, self).__init__(parent)
        self._datas = datas
        self._caption = caption
        self._objects = [data[1] for data in datas]
        self._filters = []
        self.initUI()

    def initUI(self):
        self.setSizePolicy(*[QtWidgets.QSizePolicy.Minimum] * 2)
        self.setMinimumWidth(250)
        self._filter_widget = None

        self._button = QtWidgets.QPushButton(self._caption + '  v')
        self._button.setCheckable(True)
        self._button.toggled.connect(self.on_button_toggled)

        self._label = self._create_label()
        self._scroll_area = self._create_scroll_area()

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setSpacing(3)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._button)
        self._layout.addWidget(self._scroll_area)

    def _create_label(self):
        label = QtWidgets.QLabel()
        label.setContentsMargins(5, 5, 5, 5)
        label.setAlignment(QtCore.Qt.AlignTop)
        return label

    def _create_scroll_area(self):
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(self._label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(25)
        scroll_area.setMaximumHeight(250)
        scroll_area.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        scroll_area.hide()
        return scroll_area

    def _update_label(self, filters):
        filters_to_strings = ''
        liner = 0
        for filter in filters:
            filters_to_strings += filter + ", "
            liner += len(filter) + 2
            if liner > 30:
                filters_to_strings += "\n"
                liner = 0
        self._label.setText(filters_to_strings)

    def set_filters(self, filters):
        self._filters = filters

    def set_datas(self, datas):
        self._datas = datas
        self._filters = [filter for filter in self._filters if filter in datas]
        self._update_label(self._filters)

    def close_tab(self):
        if self._button.isChecked():
            self._button.setChecked(False)

    def on_filters_changed(self, filters):
        if len(filters):
            self._scroll_area.show()
        else:
            self._scroll_area.hide()
        self._filters = filters
        self.filtersChanged.emit(filters)
        self._update_label(filters)

    def on_button_toggled(self, state):
        if not state:
            self._filter_widget.close()
            self._filter_widget = None
            return
        else:
            self.isOpened.emit()

        self._filter_widget = FitlersSelector(self._datas, self._filters)
        self._filter_widget.filtersChanged.connect(self.on_filters_changed)
        self._filter_widget.closeAsked.connect(self.close_tab)
        self._filter_widget.move(
            self.mapToGlobal(self._button.pos()).x(),
            self.mapToGlobal(self._button.pos()).y() + self._button.height())
        self._filter_widget.setFixedWidth(self._button.width())
        self._filter_widget.show()

    @property
    def filters(self):
        return self._filters


class FitlersSelector(QtWidgets.QWidget):
    filtersChanged = QtCore.pyqtSignal(list)
    closeAsked = QtCore.pyqtSignal()

    def __init__(self, datas=[], filters=[], parent=None):
        super(FitlersSelector, self).__init__(
            parent, QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Window |
            QtCore.Qt.WA_DeleteOnClose)
        self._datas = sorted(datas)
        self._filters = filters
        self.initUI()

    def initUI(self):
        self.setFocus()
        self.installEventFilter(self)
        self._widgets = self._create_widgets()

        self._check_all = QtWidgets.QPushButton(text.SELECT_ALL)
        self._check_all.clicked.connect(partial(self.check_all, 2))
        self._check_all.setFocusPolicy(QtCore.Qt.NoFocus)
        self._check_none = QtWidgets.QPushButton(text.SELECT_NONE)
        self._check_none.clicked.connect(partial(self.check_all, 0))
        self._check_none.setFocusPolicy(QtCore.Qt.NoFocus)

        self._upper_layout = self._create_upper_layout()

        self._scroll_widget = QtWidgets.QWidget()
        self._scroll_area = self._create_scroll_area()
        self._scroll_layout = QtWidgets.QVBoxLayout(self._scroll_widget)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._fill_scroll_layout()

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.addLayout(self._upper_layout)
        self._layout.addWidget(self._scroll_area)

    def _create_scroll_area(self):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.horizontalScrollBar().hide()
        scroll.setWidget(self._scroll_widget)
        scroll.setFocusPolicy(QtCore.Qt.NoFocus)
        return scroll

    def _create_widgets(self):
        widgets = []
        for data in self._datas:
            widget = QtWidgets.QCheckBox(data)
            if data in self._filters:
                widget.setCheckState(2)
            widget.setFocusPolicy(QtCore.Qt.NoFocus)
            widget.stateChanged.connect(self.on_filters_changed)
            widgets.append(widget)
        return widgets

    def _fill_scroll_layout(self):
        for widget in self._widgets:
            self._scroll_layout.addWidget(widget)

    def _create_upper_layout(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._check_all)
        layout.addWidget(self._check_none)
        return layout

    def check_all(self, int):
        for widget in self._widgets:
            widget.setCheckState(int)

    def on_filters_changed(self):
        filters = []
        for index, widget in enumerate(self._widgets):
            if widget.isChecked():
                filters.append(self._datas[index])
        self.filtersChanged.emit(filters)

    def focusOutEvent(self, _):
        self.closeAsked.emit()
        return QtWidgets.QWidget.focusOutEvent(self, _)
