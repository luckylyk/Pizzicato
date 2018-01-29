from Pizzicato.preferences import PizzicatoPreferences


class PizzicatoPreferencesController(object):

    @staticmethod
    def set_values(cls, values):
        for key in values.keys():
            setattr(cls, key, values[key])
        cls.save(PizzicatoPreferences.PREFS_FILE_PATH)
