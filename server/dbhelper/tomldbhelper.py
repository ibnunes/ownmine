import os
import configparser
import tomllib as toml


class TomlDBHelper(object):
    """
    TOML DB Class Helper: manages a TOML-based database.
    """

    def __init__(self, inipath = None, autoload = True):
        """ Initializes with a decrypted config.ini file """
        self.config = configparser.ConfigParser()
        self.err    = print
        self.data   = {}
        self.config.read(os.getcwd() + '../cfg/config.ini' if inipath is None else inipath)
        self._isloaded = False
        if autoload:
            self.load()


    def bindErrorCallback(self, errcall):
        """
        Binds a remote callback function to print out error messages.
        """
        self.err = errcall


    def load(self):
        if not self._isloaded:
            try:
                with open(self.config["DATABASE"]['database'], "rb") as f:
                    self.data = toml.load(f)
                self._isloaded = True
            except (FileNotFoundError, toml.TOMLDecodeError) as ex:
                self.err(f"Error loading configuration file '{self.config["DATABASE"]['database']}':\n\t{ex}")


    def commit(self):
        pass


