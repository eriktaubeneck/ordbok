import os
import six
from .util import create_config_file
from .config_env import ConfigEnv
from .exceptions import OrdbokMissingPrivateKeyException


class Ordbok(dict):
    def __init__(self, config_files=None, config_dir='config',
                 include_env=True, namespace='ordbok',
                 default_environment='development', **kwargs):
        self.config_files = config_files
        if not self.config_files:
            self.config_files = ['config.yml', 'local_config.yml']
        self.config_dir = config_dir
        self.include_env = include_env
        self.namespace = namespace
        self.default_environment = default_environment
        self.loaded = False
        return super(Ordbok, self).__init__(**kwargs)

    @property
    def config_cwd(self):
        if hasattr(self, '_root_path'):
            return self._root_path
        return os.getcwd()

    @property
    def config_file_names(self):
        return (
            [getattr(config_file, 'config_file_path', None)
             for config_file in self.config_files if
             hasattr(config_file, 'config_file_path')] +
            [config_file for config_file in self.config_files if
             isinstance(config_file, six.string_types)]
        )

    def load(self):
        if self.loaded:
            raise Exception('Ordbok instance can only be loaded once.')
        if not self.get('ENVIRONMENT'):
            self['ENVIRONMENT'] = os.environ.get(
                '{}_ENVIRONMENT'.format(self.namespace.upper()),
                self.default_environment).lower()

        self.config_files = [create_config_file(f) for f in self.config_files]

        for f in self.config_files:
            f.init_config(self)

        if self.include_env:
            self.config_files.append(ConfigEnv(self))

        config_files_lookup = {cf.keyword: cf for cf in self.config_files}
        for config_file in self.config_files:
            config_file.load(config_files_lookup)
        self.loaded = True

    @property
    def private_file_key(self):
        key = self.get(
            'PRIVATE_KEY_ORDBOK',
            os.environ.get(
                'ORDBOK_PRIVATE_KEY_ORDBOK',
                os.environ.get('PRIVATE_KEY_ORDBOK')
            )
        )
        if not key:
            raise OrdbokMissingPrivateKeyException
        return key
