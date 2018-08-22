#!/usr/bin/python
# -*- coding: utf-8 -*-

from Pizzicato.functions import (
    create_new_piece_folders, create_new_band_folders, rename_audio_file,
    create_printable_file, combine_audio_files_to_zip,
    combine_printables_to_pdf, rename_band)
from Pizzicato.model import PrintableFile
from Pizzicato.strings import reCamelCase
from Pizzicato.preferences import PizzicatoPreferences
from Pizzicato.views.utils import warning
import shutil
import os


class PizzicatoController(object):
    context = None
    bands_models = []
    pieces_models = []
    printable_models = []
    bands_combo_view = None

    @staticmethod
    def set_context(context):
        PizzicatoController.context = context

    @staticmethod
    def create_piece(band, name):
        create_new_piece_folders(band, name)
        folder = reCamelCase(name)
        piece = band.add_piece(folder)
        for pieces_model in PizzicatoController.pieces_models:
            pieces_model.add_piece(piece)

    @staticmethod
    def remove_piece(piece):
        piece.band.remove_piece(piece)
        shutil.rmtree(piece.path)
        for pieces_model in PizzicatoController.pieces_models:
            pieces_model.remove_piece(piece)

    @staticmethod
    def create_band(name):
        path = create_new_band_folders(
            PizzicatoController.context.working_dir, name)
        band = PizzicatoController.context.get_band_from_path(path)
        for bands_model in PizzicatoController.bands_models:
            bands_model.add_band(band)
        PizzicatoController.bands_combo_view.select_band(band)

    @staticmethod
    def rename_band(band, name):
        for bands_model in PizzicatoController.bands_models:
            bands_model.layoutAboutToBeChanged.emit()
        dst = rename_band(band, name)
        for bands_model in PizzicatoController.bands_models:
            bands_model.layoutChanged.emit()
        print(basename)

    @staticmethod
    def rename_audio_file(audio_file, name):
        audio_file.set_name(name)
        new_path = rename_audio_file(audio_file)
        audio_file.set_path(new_path)

    @staticmethod
    def set_audio_file_categorie(audio_file, file_categorie):
        audio_file.set_categorie(file_categorie)
        new_path = rename_audio_file(audio_file)
        audio_file.set_path(new_path)

    @staticmethod
    def remove_band(band):
        for bands_model in PizzicatoController.bands_models:
            bands_model.remove_band(band)
        shutil.rmtree(band.path)
        PizzicatoController.context.update()

    @staticmethod
    def add_printables_files(instruments, piece):
        for instrument in instruments:
            path = create_printable_file(instrument[0], instrument[1], piece)
            for printable_model in PizzicatoController.printable_models:
                printable_model.add_file(PrintableFile(path))
        PizzicatoController.context.update()

    @staticmethod
    def append_bands_models(model):
        return PizzicatoController.bands_models.append(model)

    @staticmethod
    def append_pieces_models(model):
        return PizzicatoController.pieces_models.append(model)

    @staticmethod
    def append_printables_model(model):
        return PizzicatoController.printable_models.append(model)

    @staticmethod
    def zip_audio_files(abstract_files, dst):
        return combine_audio_files_to_zip(abstract_files, dst)

    @staticmethod
    def merge_pdf_file(abstract_files, dst):
        return combine_printables_to_pdf(abstract_files, dst)

    @staticmethod
    def import_files(sources, destination_folder, piece):
        folder = destination_folder
        for src in sources:
            dst = os.path.join(folder, os.path.basename(src))
            # check if path exist
            if os.path.exists(dst):
                question = warning(
                    '{} already exist\nDo you wan\'t to erase it ?'.format(
                        dst), question=True)
                if not question:
                    continue
            shutil.copy(src, dst)
            PizzicatoController.context.update()

    @staticmethod
    def import_editables_files(sources, piece):
        destination_folder = os.path.join(
            piece.path, PizzicatoPreferences.EDITABLES_FOLDER)
        PizzicatoController.import_files(sources, destination_folder, piece)

    @staticmethod
    def import_audios_files(sources, piece):
        destination_folder = os.path.join(
            piece.path, PizzicatoPreferences.AUDIOS_FOLDER)
        PizzicatoController.import_files(sources, destination_folder, piece)
