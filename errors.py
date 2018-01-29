
class ComparaisonError(Exception):

    def __init__(self, object_1, object_2):
        message = (
            '{} cannot be compared to a {}'.format(
                type(object_1), type(object_2)))
        super(ComparaisonError, self).__init__(message)


class NotImplementedError(Exception):
    pass
