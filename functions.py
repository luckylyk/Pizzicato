from Pizzicato.preferences import PizzicatoPreferences, PizzicatoEnums

from subprocess import Popen
from Pizzicato.strings import reCamelCase
from PyPDF2 import PdfFileMerger
from zipfile import ZipFile, ZIP_DEFLATED

import os
import shutil


##################################################################
# os modul shortcuts                                             #
##################################################################

def osjoin(*paths):
    return os.path.normpath(os.path.join(*paths))


def ossplit(path):
    return os.path.split(path)

##################################################################
# querying                                                       #
##################################################################


def get_index_for_insertion_in_sorted_list(list_data, value):
    list_data_proxy = list_data[:]
    list_data_proxy.append(value)
    list_data_proxy = sorted(
        list_data_proxy, key=lambda data: data.name.lower())
    for index, element in enumerate(list_data_proxy):
        if element == value:
            print(list_data_proxy, value)
            return index


def get_number_of_piece_from_path(path):
    return len(get_pieces_folders_available_from_path(path))


def get_pieces_folders_available_from_path(path):
    path = osjoin(path, PizzicatoPreferences.FINALS_FOLDER)
    paths = [p for p in os.listdir(path) if os.path.isdir(osjoin(p, path))]
    piece_folders = [
        osjoin(path, folder) for folder in paths
        if is_piece_dir(osjoin(path, folder))]
    return piece_folders


def get_music_files_from_piece(piece):
    path = osjoin(piece.path, PizzicatoPreferences.AUDIOS_FOLDER)
    files = []
    for file in os.listdir(path):
        for ext in PizzicatoPreferences.AUDIOS_SUPPORTED_EXTENSIONS.extentions:
            if file.lower().endswith(ext):
                files.append(osjoin(path, file))
    return files


def get_printable_files_from_piece(piece):
    path = osjoin(piece.path, PizzicatoPreferences.PRINTABLES_FOLDER)
    files = []
    for file in os.listdir(path):
        for ext in PizzicatoPreferences.PRINTABLES_SUPPORTED_EXTENSIONS.extentions:
            if file.lower().endswith(ext):
                files.append(osjoin(path, file))
    return files


def get_editable_files_from_piece(piece):
    path = osjoin(piece.path, PizzicatoPreferences.EDITABLES_FOLDER)
    files = []
    for file in os.listdir(path):
        for ext in PizzicatoPreferences.EDITABLES_SUPPORTED_EXTENSIONS.extentions:
            if file.lower().endswith(ext):
                files.append(osjoin(path, file))
    return files


##################################################################
# Files, Folders and os operation                                #
##################################################################

def start_file(abstract_file):
    program = abstract_file.extention.bin_path
    print(program)
    print(abstract_file.path)
    Popen([program, abstract_file.path])


def open_folder_in_explorer(folder):
    return os.startfile(folder)


def create_new_piece_folders(band, name):
    dst = osjoin(
        band.path, PizzicatoPreferences.FINALS_FOLDER, reCamelCase(name))
    os.makedirs(dst)
    os.makedirs(osjoin(dst, PizzicatoPreferences.AUDIOS_FOLDER))
    os.makedirs(osjoin(dst, PizzicatoPreferences.PRINTABLES_FOLDER))
    os.makedirs(osjoin(dst, PizzicatoPreferences.EDITABLES_FOLDER))
    return dst


def create_new_band_folders(working_path, name):
    dst = osjoin(working_path, reCamelCase(name))
    os.makedirs(dst)
    os.makedirs(osjoin(dst, PizzicatoPreferences.FINALS_FOLDER))
    os.makedirs(osjoin(dst, PizzicatoPreferences.WIP_FOLDER))
    return dst


def rename_piece(piece, name):
    band_path = piece.band.path
    name_formated = reCamelCase(name)
    for printable_file in piece.get_printable_files():
        printable_file.rename(name)
    src = piece.path
    dst = osjoin(
        band_path, PizzicatoPreferences.FINALS_FOLDER, name_formated)
    os.rename(src, dst)
    return dst


def rename_band(band, name):
    src = band.path
    dst = osjoin(os.path.dirname(src), reCamelCase(name))
    os.rename(src, dst)
    return dst


def rename_audio_file(audio_file):
    src = audio_file.path
    file_folder = os.path.dirname(audio_file.path)
    file_name = audio_file.construct_filename()
    dst = (osjoin(file_folder, file_name))
    os.rename(src, dst)
    return dst


def rename_printable_file(printable_file, new_name):
    name_formated = reCamelCase(new_name)
    file_new_name = name_formated + '_' + printable_file.file.split('_')[-1]
    src = printable_file.path
    dst = osjoin(ossplit(src)[0], file_new_name)
    os.rename(src, dst)


def create_printable_file(src, instrument, piece):
    file_name = reCamelCase(piece.title) + '_' + instrument + '.pdf'
    dst = osjoin(piece.path, PizzicatoPreferences.PRINTABLES_FOLDER, file_name)
    print(src)
    print(dst)
    shutil.copyfile(src, dst)
    return dst


##################################################################
# Combines                                                       #
##################################################################


def combine_printables_to_pdf(printables, dst):
    '''
    Create a pdf file
    ::param printables : list of PrintableFile
    ::param destination : pdf destination
    '''
    if not dst.endswith('.pdf'):
        dst += '.pdf'

    merger = PdfFileMerger()
    for printable in printables:
        if printable.extention == 'pdf':
            pdf = open(printable.path, 'rb')
            merger.append(pdf)

    merger.write(dst)


def combine_audio_files_to_zip(audios, dst):
    '''
    Create a zip from abstract_files
    '''
    zipf = ZipFile(dst, 'w', ZIP_DEFLATED)
    for audio in audios:
        path = audio.path
        arcname = (
            os.path.basename(path)
            if audio.categorie == PizzicatoEnums.MUSIC_FILE_CATEGORIE_UNDEFINED
            else os.path.basename(path)[4:])
        zipf.write(path, arcname=arcname)
    zipf.close()


##################################################################
# Files, Folders and os querying                                 #
##################################################################


def is_band_dir(path):
    try:
        dirs = os.listdir(path)
        return all(
            [PizzicatoPreferences.FINALS_FOLDER in dirs,
             PizzicatoPreferences.WIP_FOLDER in dirs])
    except NotADirectoryError:
        return False


def is_piece_dir(path):
    try:
        dirs = os.listdir(path)
        return all(
            [PizzicatoPreferences.EDITABLES_FOLDER in dirs,
             PizzicatoPreferences.AUDIOS_FOLDER in dirs,
             PizzicatoPreferences.PRINTABLES_FOLDER in dirs])
    except NotADirectoryError:
        return False


##################################################################
# misc                                                           #
##################################################################

def create_audio_file_path(instrument, piece):
    return osjoin(
        piece.path, PizzicatoPreferences.EDITABLES_FOLDER,
        reCamelCase(piece.title) + '_' + instrument + '.pdf')
