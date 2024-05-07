import hashlib
import binascii

from .tomldbhelper import *
from server.ownminemgr import OwnmineManager


class DBControl(object):
    def __init__(self):
        self._helper  = TomlDBHelper()
        self._manager = OwnmineManager(self._helper.data)
        # self._helper.bindErrorCallback(crt.writeError)


    def fetchAppKey(self, appId):
        """
        Fetchs App Key.

        Args:
            appId (int): Application ID

        Returns:
            str: Application Key associated to the given App ID
        """
        keys = self._helper.data["appkeys"]
        if appId in keys:
            return keys[appId]
        return None


    def getHMACKey(self):
        """
        Gets HMAC Key from the config.

        Returns:
            str: HMAC key
        """
        return self._helper.config['VALIDATION']['hmac']

