
class XIVAPIException(Exception):
    pass


class XIVAPIConfigurationError(XIVAPIException):
    pass


class XIVAPIServerError(XIVAPIException):

    def __init__(self, description, code=0):
        super(XIVAPIServerError, self).__init__(description)
        self.code = code


class XIVAPIDataFormatError(XIVAPIException):
    pass


class XIVAPIThreadingException(XIVAPIException):
    pass
