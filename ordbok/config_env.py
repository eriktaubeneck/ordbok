import os
import yaml
from .config_file import ConfigFile
from .exceptions import OrdbokTargetedEnvKeyException


class ConfigEnv(ConfigFile):
    def __init__(self, config):
        self.config = config
        self.keyword = '{}_env_config'.format(self.config.namespace)
        self.required_keys = []
        self.keyword_lookup = {}
        self.loaded = False

    def add_required_key(self, key, value):
        if value == self.keyword:
            self.required_keys.append(key)
        elif value.startswith(self.keyword):
            self.keyword_lookup[key] = value.replace(self.keyword+'_', '')
            self.required_keys.append(key)

    def _load(self):
        environ = {
            key.replace(self.config.namespace.upper()+'_', ''): value
            for key, value in os.environ.items() if value and
            key.startswith(self.config.namespace.upper())}
        for key, value in environ.items():
            self.config[key] = yaml.load(value)

        for key, env_key in self.keyword_lookup.items():
            value = os.environ.get(env_key.upper(), None)
            if value is None:
                raise OrdbokTargetedEnvKeyException(key, env_key)
            self.config[key] = value

    def _check_required_keys(self):
        def custom_exception_gen(_, key):
            return Exception(
                '{} config key should be specified in the environment '
                'but was not found.'.format(key))
        return super(ConfigEnv, self)._check_required_keys(
            custom_exception_gen=custom_exception_gen)
