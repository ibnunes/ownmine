import hashlib
import binascii


class WrongPassword(Exception):
    """Exception WrongPassword."""
    def __init__(self, message="Wrong password"):
        self.message = message
        super().__init__(self.message)


class DBControl(object):
    def __init__(self):
        """Initializes DBControl."""
        self._helper = None     # MariaDBHelper()
        # self._helper.bindErrorCallback(crt.writeError)

