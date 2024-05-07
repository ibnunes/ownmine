import hashlib
import json
import hmac

from dbhelper.dbcontrol import *


class AppIdNotFound(Exception):
    """Exception that indicates that it cannot find App ID."""
    def __init__(self, message="App ID not found"):
        self.message = message
        super().__init__(self.message)


class AppAuthHeaderNotFound(Exception):
    """Exception that indicates that it cannot find Auth Header."""
    def __init__(self, message="App authentication header not found"):
        self.message = message
        super().__init__(self.message)


class InvalidAppAuthenticationChallenge(Exception):
    """Exception that indicates that the app authentication challenge is invalid."""
    def __init__(self, message="Invalid app authentication challenge"):
        self.message = message
        super().__init__(self.message)


class NotConnected(Exception):
    """Exception that indicates that it is not connected."""
    def __init__(self, message="Unable to connect to database"):
        self.message = message
        super().__init__(self.message)


class AppAuthenticationServer(object):
    def __init__(self, db = None):
        """Initializes AppAuthenticationServer()"""
        self._db = DBControl() if db is None else db


    def authenticateApp(self, headers, method="GET", body=None):
        """
        Autenticates App.

        Args:
            headers (Headers): [description]
            method (str, optional): Method. Defaults to "GET".
            body (dict, optional): Body. Defaults to None.

        Raises:
            AppIdNotFound: Exception that indicates that it cannot find App ID.
            InvalidAppAuthenticationChallenge: Exception that indicates that the app authentication challenge is invalid.
            NotConnected: Exception that indicates that it is not connected.
            AppAuthHeaderNotFound: Exception that indicates that it cannot find Auth Header.

        Returns:
            True: If the signature is correct
        """
        try:
            appid     = headers["appid"]
            appKey    = self._db.fetchAppKey(appid)
            timestamp = headers["timestamp"]
            nonce     = headers["nonce"]
            sign      = headers["sig"]

            if appKey is None:
                raise AppIdNotFound()

            if method == "GET":
                if self.compareGetSig(timestamp, nonce, appid, appKey, sign):
                    return True
            elif method == "POST":
                if self.generatePostSig(timestamp, nonce, appid, appKey, sign, body):
                    return True
            elif method == "PATCH":
                if self.comparePatchSig(timestamp, nonce, appid, appKey, sign, body):
                    return True
            raise InvalidAppAuthenticationChallenge()
        # except ConnectionNotEstablished:
        #     raise NotConnected()
        except KeyError:
            raise AppAuthHeaderNotFound()


    def getHeaders(self, request):
        """
        Gets Headers.

        Args:
            request (Request): Request given

        Raises:
            AppAuthHeaderNotFound: Exception that indicates that it cannot find Auth Header.

        Returns:
            (int,float,str,str): App ID, Time Stamp, Nonce, Signature
        """
        try:
            appid = request.headers['appid']
            timestamp = request.headers['timestamp']
            nonce = request.headers['nonce']
            sign = request.headers['sig']
            return (appid, timestamp, nonce, sign)
        except KeyError:
            raise AppAuthHeaderNotFound()


    def generatePostSig(self, timestamp, nonce, appId, key, hsig, body):
        """
        Compares POST signature.

        Args:
            timestamp (float): Time Stamp
            nonce (Any): ?
            appId (Any): ?
            key (Any):   ?
            hsig (Any):  ?
            body (Any):  ?

        Returns:
            bool: True if same
        """
        bodyHash = hashlib.sha256(json.dumps(body).encode('utf-8')).hexdigest()
        sign = f"{appId}POST{timestamp}{nonce}{bodyHash}"
        hmacsh256 = hmac.new(
            key=key.encode('utf-8'),
            msg=sign.encode('utf-8'),
            digestmod=hashlib.sha256
        )

        return hmacsh256.hexdigest() == hsig


    def comparePatchSig(self, timestamp, nonce, appId, key, hsig, body):
        """
        Compares PATCH signature.

        Args:
            timestamp (float): Time Stamp
            nonce (Any): ?
            appId (Any): ?
            key (Any):   ?
            hsig (Any):  ?
            body (Any):  ?

        Returns:
            bool: True if same
        """
        bodyHash = hashlib.sha256(json.dumps(body).encode('utf-8')).hexdigest()
        sign = f"{appId}PATCH{timestamp}{nonce}{bodyHash}"

        hmacsh256 = hmac.new(
            key = key.encode('utf-8'),
            msg = sign.encode('utf-8'),
            digestmod = hashlib.sha256
        )

        return hmacsh256.hexdigest() == hsig


    def compareGetSig(self, timestamp, nonce, appId, key, hsig):
        """
        Compares GET signature.

        Args:
            timestamp (float): Time Stamp
            nonce (Any): ?
            appId (Any): ?
            key (Any):   ?
            hsig (Any):  ?

        Returns:
            bool: True if same
        """
        sign = f"{appId}GET{timestamp}{nonce}"

        hmacsh256 = hmac.new(
            key = key.encode('utf-8'),
            msg = sign.encode('utf-8'),
            digestmod = hashlib.sha256
        )

        return hmacsh256.hexdigest() == hsig
