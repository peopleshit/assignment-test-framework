from cryptography.fernet import Fernet

from core.repository import Keystore


def _encrypt(key: any, text: str) -> str:
    encoded_text = text.encode()

    f = Fernet(key)

    return f.encrypt(encoded_text).decode()


def _decrypt(key: any, text: str) -> str:
    encrypted = text.encode()

    f = Fernet(key)

    return f.decrypt(encrypted).decode()


class EncryptionUtil(object):
    def __init__(self, keystore: Keystore):
        self.__keystore = keystore

    def encrypt(self, text: str):
        return self.__keystore.execute(_encrypt, text)

    def decrypt(self, text: str):
        return self.__keystore.execute(_decrypt, text)
