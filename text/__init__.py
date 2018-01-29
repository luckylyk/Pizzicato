from Pizzicato.preferences import PizzicatoPreferences

index = PizzicatoPreferences.LANGUAGES_INDEX


if PizzicatoPreferences.LANGUAGES_AVAILABLES[index] == 'english':
    from Pizzicato.text.english import *

if PizzicatoPreferences.LANGUAGES_AVAILABLES[index] == 'french':
    from Pizzicato.text.french import *