import os
from typing import Optional
from cryptography.fernet import Fernet

DEFAULT_SECRET_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'ownmine.key')


class OwnmineSecret:

    def __init__(self, key_path: str = DEFAULT_SECRET_PATH, create_key_if_unavailable: bool = True):
        self.key_path = key_path
        if not self.key_exists() and create_key_if_unavailable:
            self.generate_key()


    def key_exists(self):
        return os.path.exists(self.key_path)


    def is_encrypted(self, password: str) -> bool:
        return password.startswith("gAAAA") and len(password) >= 100


    def generate_key(self, force = False):
        if self.key_exists() and not force:
            return
        key = Fernet.generate_key()
        with open(self.key_path, "wb") as f:
            f.write(key)


    def get_key(self):
        with open(self.key_path, "rb") as f:
            return f.read()


    def encrypt(self, password: str) -> str:
        fernet = Fernet(self.get_key())
        return fernet.encrypt(password.encode()).decode()


    def decrypt(self, token: str) -> str:
        fernet = Fernet(self.get_key())
        return fernet.decrypt(token.encode()).decode()

