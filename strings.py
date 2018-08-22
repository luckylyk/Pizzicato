def unCamelCase(name):
    '''
    Format CamelCase String for better Readability
    '''
    reformated_name = ''
    check = "0123456789' ,_.-"

    for posLet, letter in enumerate(name):
        if posLet == 0:
            reformated_name += letter

        elif letter == ',':
            reformated_name += letter

        elif name[posLet - 1] == ',':
            reformated_name += " " + letter

        elif letter not in check[:9] and name[posLet - 1] in check[:9]:
            reformated_name += " " + letter

        elif letter == letter.upper() and letter not in check and name[posLet - 1] not in check:
            reformated_name += " " + letter

        else:
            reformated_name += letter

    if reformated_name.endswith('/'):
        reformated_name = reformated_name[0:(len(reformated_name) - 1)]

    if reformated_name.endswith('\\'):
        reformated_name = reformated_name[0:(len(reformated_name) - 2)]
    reformated_name = reformated_name.strip()

    return reformated_name


def reCamelCase(name, force_first=False):
    '''
    Format string to CamelCase
    '''
    reformated_name = ''
    for pos, letter in enumerate(name):
        if force_first and pos == 0:
            reformated_name += letter.upper()
            continue
        if letter == ' ':
            continue
        if name[pos - 1] == ' ' and pos != 0:
            reformated_name += letter.upper()
        elif pos == 0:
            reformated_name += letter
        else:
            reformated_name += letter

    # delete a final slash
    if reformated_name.endswith('/'):
        reformated_name = reformated_name[0:(len(reformated_name) - 1)]
    # delete a final backslash
    if reformated_name.endswith('\\'):
        reformated_name = reformated_name[0:(len(reformated_name) - 2)]
    reformated_name = reformated_name.strip()
    return reformated_name


def find_closer_string_in_list(string, strings):
    '''
    :param: string : is a simple string (short preferably)
    :param: strings : is a list of strings objects (all short)

    this fonction compare the string to all strings and
    return the closest in list 

    '''
    likeness_scores = {}

    string_clean = string.replace('.', '').replace(
        ' ', '').replace('_', '').lower()
    string_words_list = string.lower().split(' ')

    for s in strings:
        list_tmp = unCamelCase(s).lower().split(' ')
        word_checker = s.replace('.', '').replace(
            ' ', '').replace('_', '').lower()
        loop = range(len(string_clean))
        likeness_word_score = sum(
            [1 for word in string_words_list if word in list_tmp])
        likeness_dubblet_score = sum(
            [1 for i in loop if string_clean[i:i + 2] in word_checker])
        likeness_triplet_score = sum(
            [1 for i in loop if string_clean[i:i + 3] in word_checker])
        likeness_quadruplet_score = sum(
            [1 for i in loop if string_clean[i:i + 4] in word_checker])
        likeness_quintuplet_score = sum(
            [1 for i in loop if string_clean[i:i + 5] in word_checker])

        final_score = (
            (likeness_word_score * 15) + likeness_dubblet_score * 2 +
            (likeness_triplet_score * 4) + (likeness_quadruplet_score * 6) +
            (likeness_quintuplet_score * 8)
        )

        likeness_scores[s] = final_score

    best_score = sorted(likeness_scores.values())[-1]
    string_associated = list(likeness_scores.keys())[
        list(likeness_scores.values()).index(best_score)]

    return (string_associated)
