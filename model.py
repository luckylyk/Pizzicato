from Pizzicato.preferences import PizzicatoPreferences, PizzicatoEnums
from Pizzicato.errors import ComparaisonError
from Pizzicato.functions import (
    osjoin, ossplit, get_pieces_folders_available_from_path,
    get_number_of_piece_from_path, get_music_files_from_piece,
    get_printable_files_from_piece, get_editable_files_from_piece,
    rename_piece, rename_printable_file)

import os
import pickle
import json
from PyQt4.QtCore import QObject
from StringOprations import unCamelCase

ROOT = os.path.dirname(__file__)


class PizzicatoContext(object):

    def __init__(self, path):
        self._path = path
        self._bands = self._get_all_bands()
        self._pieces = self._get_all_pieces()
        self._printables = self._get_all_printables()

    def _get_all_printables(self):
        printables = []
        for piece in self._pieces:
            printables += piece.get_printable_files()
        return printables

    def _get_all_pieces(self):
        pieces = []
        for band in self._bands:
            pieces += band.pieces
        return pieces

    def _get_all_bands(self):
        paths = [
            path for path in os.listdir(self._path)
            if os.path.isdir(os.path.join(self._path, path))]
        return [Band(osjoin(self._path, folder)) for folder in paths]

    def __str__(self):
        return '\n\n'.join([str(band) for band in self._bands])

    def update(self):
        self._bands = self.get_bands()

    def get_band_from_path(self, path):
        return Band(path)

    @property
    def bands(self):
        return self._bands

    @property
    def pieces(self):
        return self._pieces

    @property
    def printables(self):
        return self._printables

    @property
    def audios(self):
        audios_files = []
        for piece in self._pieces:
            piece_audios = piece.get_audio_files()
            audios_files += piece_audios if piece_audios else []
        return audios_files

    @property
    def working_dir(self):
        return self._path

    def update(self):
        self._bands = self._get_all_bands()
        self._pieces = self._get_all_pieces()
        self._printables = self._get_all_printables()


class Band(object):

    def __init__(self, path):
        self._path = path
        self._name = unCamelCase(ossplit(path)[-1])
        self._pieces = [
            Piece(piece, parent=self)
            for piece in get_pieces_folders_available_from_path(self._path)]
        self._instruments = self._get_instruments()

    def update(self):
        self._name = unCamelCase(ossplit(self._path)[-1])
        self._pieces = [
            Piece(piece, parent=self)
            for piece in get_pieces_folders_available_from_path(self._path)]

    @property
    def wip_folder(self):
        return osjoin(self.path, PizzicatoPreferences.WIP_FOLDER)

    @property
    def finals_folder(self):
        return osjoin(self.path, PizzicatoPreferences.FINALS_FOLDER)

    @property
    def pieces(self):
        return self._pieces

    def add_piece(self, folder):
        folder = osjoin(self._path, PizzicatoPreferences.FINALS_FOLDER, folder)
        piece = Piece(folder, parent=self)
        self._pieces.append(piece)
        self._pieces = sorted(self._pieces, key=lambda piece: piece.title)
        return piece

    def remove_piece(self, piece):
        self._pieces.remove(piece)

    def _get_instruments(self):
        instruments = []
        for piece in self._pieces:
            instruments += piece.instruments
        instruments = set(instruments)
        return instruments

    @property
    def instruments(self):
        return sorted(list(self._instruments))

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path
        self._update()

    @property
    def name(self):
        return self._name

    @property
    def piece_number(self):
        return get_number_of_piece_from_path(self._path)

    def __str__(self):
        string = self._name + '(contain {} pieces)'.format(
            len(self._pieces))
        string += '\n   ---> '
        string += '\n   ---> '.join([piece.name for piece in self._pieces])
        return string

    def __eq__(self, other):
        if isinstance(other, Band):
            return object.__eq__(self.name, other.name)
        else:
            raise ComparaisonError(self, other)

    def __lt__(self, other):
        if isinstance(other, Band):
            return object.__lt__(self.name, other.name)
        else:
            raise ComparaisonError(self, other)

    def __le__(self, other):
        if isinstance(other, Band):
            return object.__le__(self.name, other.name)
        else:
            raise ComparaisonError(self, other)

    def __gt__(self, other):
        if isinstance(other, Band):
            return object.__gt__(self.name, other.name)
        else:
            raise ComparaisonError(self, other)

    def __ge__(self, other):
        if isinstance(other, Band):
            return object.__ge__(self.name, other.name)
        else:
            raise ComparaisonError(self, other)


class Piece(object):

    def __init__(self, path, parent=None):
        self._init_attributes(path)
        self._band = parent

    def _init_attributes(self, path):
        self._path = path
        self._name = unCamelCase(ossplit(path)[-1])
        self._options = PieceProperties(
            name=self._name, file=osjoin(
                path, PizzicatoPreferences.PIECE_PROPERTIES_FILENAME))
        self._is_saved = True

    @property
    def arranger(self):
        return self._options.arranger

    @property
    def author(self):
        return self._options.composer

    @property
    def band(self):
        return self._band

    @property
    def comment(self):
        return self._options.comment

    @property
    def composer(self):
        return self._options.composer

    @property
    def instruments(self):
        return [file.instrument for file in self.get_printable_files()]

    @property
    def mood(self):
        return self._options.mood

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def priority(self):
        return self._options.priority

    @property
    def solists(self):
        return self._options.solists

    @property
    def style(self):
        return self._options.style

    @property
    def tempo(self):
        return self._options.tempo

    @property
    def title(self):
        return self._name

    def set_arranger(self, arranger):
        self._options.arranger = arranger

    def set_author(self, author):
        self.set_composer(author)

    def set_comment(self, comment):
        self._options.comment = comment

    def set_composer(self, composer):
        self._options.composer = composer

    def set_mood(self, mood):
        self._options.mood = mood

    def set_priority(self, priority):
        self._options.priority = priority

    def set_solists(self, solists):
        self._options.solists = solists

    def set_style(self, style):
        self._options.style = style

    def set_tempo(self, tempo):
        self._options.tempo = tempo

    def set_unsaved(self):
        self._is_saved = False

    def is_saved(self):
        return self._is_saved

    def get_audio_files(self):
        return [
            AudioFile(file, piece=self) for file in get_music_files_from_piece(self)]

    def get_printable_files(self):
        return [
            PrintableFile(file, piece=self)
            for file in get_printable_files_from_piece(self)]

    def get_editable_files(self):
        return [
            EditableFile(file, piece=self)
            for file in get_editable_files_from_piece(self)]

    def save_properties(self):
        self._is_saved = True
        return self._options.save()

    def __str__(self):
        return 'Piece object --> {}'.format(self._options)

    def rename(self, name):
        path = rename_piece(self, name)
        self._init_attributes(path)

    def __eq__(self, other):
        if isinstance(other, Piece):
            return object.__eq__(self, other)
        else:
            try:
                object.__eq__(self, other)
            except:
                raise ComparaisonError(self, other)

    def __lt__(self, other):
        if isinstance(other, Piece):
            return object.__lt__(self, other)
        else:
            raise ComparaisonError(self, other)

    def __le__(self, other):
        if isinstance(other, Piece):
            return object.__le__(self, other)
        else:
            raise ComparaisonError(self, other)

    def __gt__(self, other):
        if isinstance(other, Piece):
            return object.__gt__(self, other)
        else:
            raise ComparaisonError(self, other)

    def __ge__(self, other):
        if isinstance(other, Piece):
            return object.__ge__(self, other)
        else:
            raise ComparaisonError(self, other)

    def __repr__(self):
        return self._name


class PieceProperties(object):

    def __init__(self, file='', name=''):
        self.name = name
        self._file = file
        if self._file == '':
            raise NameError(
                u'impossible to connect to file if no path specified')
        if os.path.exists(file):
            self._load_values()
        else:
            self._init_default_values()

    def _load_values(self):
        with open(self._file, 'r') as fichier:
            loaded_properties = json.load(fichier)
            self.lenght = loaded_properties['lenght']
            self.priority = loaded_properties['priority']
            self.tempo = loaded_properties['tempo']
            self.mood = loaded_properties['mood']
            self.solists = loaded_properties['solists']
            self.style = loaded_properties['style']
            self.composer = loaded_properties['composer']
            self.arranger = loaded_properties['arranger']
            self.comment = loaded_properties['comment']
            self.is_default = loaded_properties['is_default']

    def _init_default_values(self):
        self.lenght = {'default': None,
                       'short version': None,
                       'extended version': None}
        self.priority = 2
        self.tempo = '92'
        self.mood = 2
        self.solists = []
        self.style = ''
        self.composer = ''
        self.arranger = ''
        self.comment = ''
        self.is_default = True
        self.save()

    def save(self):
        folder = os.path.split(self._file)[0]
        if not os.path.exists(folder):
            os.makedirs(folder)

        print(self.to_dict())
        with open(self._file, 'w') as fichier:
            json.dump(self.to_dict(), fichier)
        print('{} properties saved'.format(self.name))
        print(self)

    def __str__(self):
        return (
            'name = {}\nlength = {}\npriority = {}\ntempo = {}\nmood = '
            '{}\nsolists = {}\nstyle = {}\n'.format(
                self.name, self.lenght, self.priority, self.tempo,
                self.mood, self.solists, self.style))

    def __repr__(self):
        return self.name

    def __eq__(self, a):
        return self.name.__eq__(a)

    def to_dict(self):
        attributes = [
            'lenght', 'priority', 'tempo', 'mood', 'solists', 'style',
            'composer', 'arranger', 'comment', 'is_default']
        return {
            attribute: self.__getattribute__(attribute)
            for attribute in attributes}


class AbstractFile(object):

    def __init__(self, path, piece=None):
        self._path = path
        self._file = os.path.basename(path)
        self._piece = piece

    @property
    def path(self):
        return self._path

    def set_path(self, path):
        self._path = path

    @property
    def file(self):
        return self._file

    @property
    def extention(self):
        extention = self._path.split('.')[-1].lower()
        return PizzicatoPreferences.EXTENTIONS.get_from_string(extention)

    @property
    def program(self):
        return self.extention.program

    @property
    def piece(self):
        return self._piece


class AudioFile(AbstractFile):

    def __init__(self, path, piece=None):
        super(AudioFile, self).__init__(path, piece)
        self._name = self._get_name()
        self._categorie = self._get_categorie()

    def _get_name(self):
        name = self._file[:-4]
        if name[:3] in PizzicatoEnums.MUSIC_FILE_CATEGORIES.keys():
            name = name[4:]
        name = name.replace('_', ' ')
        return name

    def _get_categorie(self):
        try:
            return PizzicatoEnums.MUSIC_FILE_CATEGORIES[self._file.split('_')[0]]
        except KeyError:
            return PizzicatoEnums.MUSIC_FILE_CATEGORIE_UNDEFINED

    def __str__(self):
        return str((self._file, self.type, self.name))

    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    @property
    def ext(self):
        return self.extention.extention

    @property
    def categorie(self):
        return self._categorie

    def set_categorie(self, file_categorie):
        self._categorie = file_categorie

    def construct_filename(self):
        prefixe = (
            PizzicatoEnums.MUSIC_FILE_CATEGORIES_INVERTED[self.categorie]
            if self.categorie != PizzicatoEnums.MUSIC_FILE_CATEGORIE_UNDEFINED
            else None)

        name = ''
        if prefixe:
            name += prefixe + '_'
        name += self._name + '.' + self.extention.extention
        return name


class PrintableFile(AbstractFile):

    def __init__(self, path, piece=None):
        super(PrintableFile, self).__init__(path, piece)
        self._instrument = self._get_instrument()

    def _get_instrument(self):
        return unCamelCase(ossplit(self._path)[-1].split('_')[-1][:-4])

    @property
    def instrument(self):
        return self._instrument

    @property
    def type(self):
        return self._path[-3:]

    @property
    def title(self):
        return self.piece.title

    def rename(self, name):
        rename_printable_file(self, name)
        self._instrument = self._get_instrument()


class EditableFile(AbstractFile):

    def __init__(self, path, piece=None):
        super(EditableFile, self).__init__(path, piece)

    @property
    def file(self):
        if len(self._file) < 20:
            return self._file
        else:
            return self._file[:18] + '...'

    @property
    def program(self):
        return self.extention.program

    @property
    def description(self):
        return self.extention.extention_description
