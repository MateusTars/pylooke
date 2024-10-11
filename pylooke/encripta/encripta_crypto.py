import hashlib

from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding

class EncriptaCrypto:
    """
    EncriptaCrypto class for handling AES encryption of data, such as user or device identifiers.
    This class was reverse from the APK package br.com.encripta.looke.
    """
    def __init__(self):
        """
        Initializes the EncriptaCrypto class by generating an encryption key.
        """
        self.key: bytes = self.generate_encryption_key()

    def encrypt(self, data: str) -> bytes:
        """
        Encrypts the given data using AES encryption in CBC mode.

        :param data: The plaintext string to be encrypted.

        :return: Encrypted data.
        """
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.key)
        plaintext = Padding.pad(data.encode("utf-8"), AES.block_size)
        ciphertext = cipher.encrypt(plaintext)
        return ciphertext

    @staticmethod
    def generate_encryption_key(password: str = "kkS2mm", salt: str = "Truetech PlayReady Salt") -> bytes:
        """
        Generates a 16-byte AES key using PBKDF2-HMAC-SHA1 based on the provided password and salt.

        :param password: The password string used in the key derivation process.
        :param salt: The salt string used in the key derivation process for added security.

        :return: Encryption key.
        """
        key = hashlib.pbkdf2_hmac(
            hash_name="sha1",
            password=password.encode("utf-8"),
            salt=salt.encode("utf-8"),
            iterations=1000,
            dklen=16
        )
        return key