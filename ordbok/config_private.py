import os
import six
import yaml
import simplecrypt
from .config_file import ConfigFile
from .exceptions import (
    OrdbokMissingPrivateConfigFile, OrdbokMissingEncryptedPrivateConfigFile)


def open_wrapper(*args, **kwargs):
    '''
    This is a dumb hack used so that that these specific open calls
    can be used with fudge.patch in the tests without messing up Crypto.
    '''
    return open(*args, **kwargs)


class PrivateConfigFile(ConfigFile):
    def _load_yaml(self):
        content = self._load_and_decrypt_file()
        c = yaml.load(content)
        self._validate_yaml_content(c)
        return c

    def _load_encrypted_file(self):
        try:
            with open_wrapper(self.config_file_path + u'.private', 'rb') as f:
                return f.read()
        except IOError:
            if os.path.exists(self.config_file_path):
                raise OrdbokMissingEncryptedPrivateConfigFile(self)
            else:
                raise OrdbokMissingPrivateConfigFile(self)

    def _load_decrypted_file(self):
        try:
            with open_wrapper(self.config_file_path, 'r+') as f:
                return f.read()
        except IOError:
            raise OrdbokMissingPrivateConfigFile(self)

    def _save_encrypted_file(self):
        content = self._load_decrypted_file()
        content = self._encrypt_content(content)
        with open_wrapper(self.config_file_path+'.private', 'wb') as f:
            f.write(content)

    def _save_decrypted_file(self):
        content = self._load_and_decrypt_file()
        with open_wrapper(self.config_file_path, 'w') as f:
            f.write(content)

    def _load_and_decrypt_file(self):
        content = self._load_encrypted_file()
        return self._decrypt_content(content)

    def _decrypt_content(self, content):
        content = simplecrypt.decrypt(self.config.private_file_key, content)
        if six.PY2:
            return content
        else:
            return str(content.decode('utf8'))

    def _encrypt_content(self, content):
        return simplecrypt.encrypt(self.config.private_file_key, content)
