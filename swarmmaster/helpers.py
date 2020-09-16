

class ClientException(Exception):
    pass

class UnknownMessageException(Exception):
    pass

class EmptyMessageException(Exception):
    def __init__(self, msg=""):
        self.msg =msg