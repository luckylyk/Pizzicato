from Pizzicato.extentions import extentions, FilesExtentionList
from QtOptimizers import PreLoadedIcons
import pickle
import os


class PizzicatoPreferences (object):
    LANGUAGES_INDEX = 1
    LANGUAGES_AVAILABLES = "english", "french"

    AUDIOS_FOLDER = 'AUDIOS'
    PRINTABLES_FOLDER = 'PRINTABLES'
    EDITABLES_FOLDER = 'EDITABLES'
    FINALS_FOLDER = 'FINALS'
    WIP_FOLDER = 'WIP'
    PIECE_PROPERTIES_FILENAME = '.pieceProperties'

    EXTENTIONS = extentions
    AUDIOS_SUPPORTED_EXTENSIONS = FilesExtentionList.filtered(
        EXTENTIONS, ('mid', 'mp3', 'wav'))
    PRINTABLES_SUPPORTED_EXTENSIONS = FilesExtentionList.filtered(
        EXTENTIONS, ('pdf'))
    EDITABLES_SUPPORTED_EXTENSIONS = FilesExtentionList.filtered(
        EXTENTIONS, ('mus', 'musx', 'sib', 'mscz', 'mscx', 'xml'))

    PREFS_FILE_PATH = os.path.join(
        'c:', os.environ['HOMEPATH'], 'PizzicatoPreferences')
    CURRENT_WORKING_DIR = "D:/Works/Arrangement/MyBands_temp"

    @staticmethod
    def load(path):
        if not os.path.exists(path):
            print('No preferences saved')
            return
        with open(path, mode='rb') as prefs_file:
            prefs = pickle.Unpickler(prefs_file)
            loaded = prefs.load()
            if not isinstance(loaded, dict):
                raise TypeError()
            for key in loaded.keys():
                setattr(PizzicatoPreferences, key, loaded[key])

    @staticmethod
    def save(path):
        dumpable_type = (int, str, list, dict, float)
        pizz_dict = PizzicatoPreferences.__dict__
        to_dump = {
            key: pizz_dict[key] for key in pizz_dict
            if type(pizz_dict[key]) in dumpable_type}

        with open(path, mode='wb') as prefs_file:
            prefs = pickle.Pickler(prefs_file)
            prefs.dump(to_dump)


class PizzicatoEnums(object):
    MUSIC_FILE_CATEGORIES = {
        'ORI': 'original',
        'MAQ': 'maquette',
        'DIV': 'divers'}
    MUSIC_FILE_CATEGORIES_INVERTED = {
        'original': 'ORI',
        'maquette': 'MAQ',
        'divers': 'DIV'}
    MUSIC_FILE_CATEGORIE_UNDEFINED = 'undefined'

    TEMPI = [
        '42', '44', '46', '48', '50', '52', '54', '56', '58', '60', '63', '66',
        '69', '72', '76', '80', '84', '88', '92', '96', '100', '104', '108',
        '112', '116', '120', '126', '132', '138', '144', '152', '160', '168',
        '176', '184', '192', '200', '208']
    MOODS = ['very sad', 'sad', 'normal', 'fun', 'very fun']
    PRIORITY = [
        'abandonned', 'only for long setlist', 'sometime', 'often', 'essential']


icons = PreLoadedIcons(
    os.path.join(os.path.dirname(__file__), 'graphics'), size_limit=2046)
