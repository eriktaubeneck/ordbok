import os
import six
from .config_file import ConfigFile
from .config_env import ConfigEnv


class Ordbok(dict):
    def __init__(self, **kwargs):
        self.set_defaults(**kwargs)
        return super(Ordbok, self).__init__(**kwargs)

    def set_defaults(self, **kwargs):
        self.config_files = []
        self.config_dir = kwargs.get('config_dir', 'config')
        self.custom_config_files = kwargs.get(
            'custom_config_files', ['config.yml', 'local_config.yml'])
        self.include_env = kwargs.get('include_env', True)
        self.near_miss_key = kwargs.get('near_miss_key', 'ordbok')
        self.default_environment = kwargs.get(
            'default_environment', 'development')

    def update_defaults(self, **kwargs):
        self.config_dir = kwargs.get('config_dir', self.config_dir)
        self.custom_config_files = kwargs.get(
            'custom_config_files', self.custom_config_files)
        self.include_env = kwargs.get('include_env', self.include_env)
        self.near_miss_key = kwargs.get('near_miss_key', self.near_miss_key)
        self.default_environment = kwargs.get(
            'default_environment', self.default_environment)

    @property
    def config_cwd(self):
        return os.getcwd()

    @property
    def config_file_names(self):
        return [getattr(config_file, 'config_file_path', None)
                for config_file in self.config_files if
                getattr(config_file, 'config_file_path', None)]

    def load(self):
        if not self.get('ENVIRONMENT'):
            self['ENVIRONMENT'] = os.environ.get(
                '{}_ENVIRONMENT'.format(self.near_miss_key.upper()),
                self.default_environment).lower()

        self.config_files = [f for f in self.custom_config_files
                             if isinstance(f, ConfigFile)]
        for f in self.config_files:
            f.init_config(self)

        self.config_files.extend(
            [ConfigFile(f, self) for f in self.custom_config_files
             if isinstance(f, six.string_types)])

        if self.include_env:
            self.config_files.append(ConfigEnv(self))

        config_files_lookup = {cf.keyword: cf for cf in self.config_files}
        for config_file in self.config_files:
            config_file.load(config_files_lookup)

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
            raise Exception(
                'PRIVATE_KEY_ORDBOK config variable not found. '
                'Please set in configuration loaded before PrivateConfigFile '
                'or in the OS environment as PRIVATE_KEY_ORDBOK.'
            )
        return key
