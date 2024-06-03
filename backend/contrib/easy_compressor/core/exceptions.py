class Error(Exception):
    pass


class ImproperlyConfigured(Error):
    """ somehow improperly configured"""
    pass


class InvalidCompressorSchemaError(Error):
    pass



