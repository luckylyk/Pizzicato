

class FilesExtentionList(list):

    def __init__(self, my_list=[]):
        super(FilesExtentionList, self).__init__(my_list)

    @staticmethod
    def filtered(files_extention_list, filters):
        filtered = [
            file_extention for file_extention in files_extention_list
            if file_extention.extention in filters]
        return FilesExtentionList(filtered)

    def append(self, files_extention):
        if not isinstance(files_extention, FilesExtention):
            raise ValueError(
                'EditablesFilesExtentionList can only append '
                'EditablesFilesExtention object')
        return list.append(self, files_extention)

    @property
    def extentions(self):
        return [
            file_extension.extention
            for file_extension in self]

    def is_url_extention_in_list(self, url):
        url = url.toString()
        extention = url.split('.')[-1]
        return extention in self.extentions

    def get_from_string(self, string):
        for extention in self:
            if extention.extention == string:
                return extention


class FilesExtention(object):

    def __init__(self, program='', extention='',
                 extention_full_name='', program_bin_path=''):
        self._extention = extention.lower()
        self._program = program
        self._extention_full_name = extention_full_name
        self._program_bin_path = program_bin_path

    @property
    def extention(self):
        return self._extention

    @property
    def program(self):
        return self._program

    @property
    def extention_description(self):
        return self._extention_full_name

    @property
    def bin_path(self):
        return self._program_bin_path

    def __str__(self):
        return '\n'.join([
            self._extention, self._program, self._extention_full_name,
            str(self._program_bin_path)])

    def __eq__(self, value):
        if isinstance(value, str):
            return value.lower() == self.extention

        if isinstance(value, FilesExtentionList):
            return value.extention == self.extention

        raise TypeError(
            'Impossible to compare {} and {}\n'
            'Can only compare FileExtention with '
            'FileExtention and String'.format(type(self), type(value)))

extentions = FilesExtentionList(
    [FilesExtention(**files_extention)
        for files_extention in (
            {'program': 'Finale',
             'extention': 'mus',
             'extention_full_name': 'Finale Legacy Notation File',
             'program_bin_path': r"C:\Program Files (x86)\Finale 2014\Finale.exe"
             },
            {'program': 'Finale',
             'extention': 'musx',
             'extention_full_name': 'Finale Notation File',
             'program_bin_path': r"C:\Program Files (x86)\Finale 2014\Finale.exe"
             },
            {'program': 'Sibelius',
             'extention': 'sib',
             'extention_full_name': 'Sibelius File',
             'program_bin_path': None
             },
            {'program': 'MuseScore',
             'extention': 'mscz',
             'extention_full_name': 'Open Musescore File (zip)',
             'program_bin_path': r'C:\Program Files (x86)\MuseScore 2\bin\MuseScore.exe'
             },
            {'program': 'MuseScore',
             'extention': 'mscx',
             'extention_full_name': 'Binary Musescore File',
             'program_bin_path': r'C:\Program Files (x86)\MuseScore 2\bin\MuseScore.exe'
             },
            {'program': 'Universal',
             'extention': 'xml',
             'extention_full_name': 'Universal MusicXML',
             'program_bin_path': r'C:\Program Files (x86)\MuseScore 2\bin\MuseScore.exe'
             },
            {'program': 'Microsoft Edge',
             'extention': 'pdf',
             'extention_full_name': 'Portable Document Format',
             'program_bin_path': r"C:\Windows\explorer.exe"
             },
            {'program': 'Windows Media PLayer',
             'extention': 'mid',
             'extention_full_name': 'Musical Instrument Digital Interface',
             'program_bin_path': r"C:/Program Files (x86)/Windows Media Player/wmplayer.exe"
             },
            {'program': 'Windows Media PLayer',
             'extention': 'mp3',
             'extention_full_name': 'MPEG-1/2 Audio Layer III',
             'program_bin_path': r"C:/Program Files (x86)/Windows Media Player/wmplayer.exe"
             },
            {'program': 'Windows Media PLayer',
             'extention': 'wav',
             'extention_full_name': 'WAVEform audio file format',
             'program_bin_path': r"C:/Program Files (x86)/Windows Media Player/wmplayer.exe"
             },
    )])
