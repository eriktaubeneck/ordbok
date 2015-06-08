import os
import yaml
import six
from .exceptions import (
    OrdbokLowercaseKeyException, OrdbokMissingConfigFileException,
    OrdbokAmbiguousConfigFileException, OrdbokSelfReferenceException,
    OrdbokPreviouslyLoadedException, OrdbokNestedRequiredKeyException,
    OrdbokMissingKeyException)


class ConfigFile(object):
    def __init__(self, filename, envs=None):
        self.filename = filename
        self.envs = envs

    def init_config(self, config):
        self.config = config
        self.keyword = '{}_{}'.format(
            self.config.namespace, os.path.splitext(self.filename)[0])
        self.required_keys = []
        self.config_file_path = os.path.join(
            self.config.config_cwd, self.config.config_dir, self.filename)
        self.loaded = False

    def load(self, config_files_lookup):
        self.config_files_lookup = config_files_lookup
        self._load()
        self._check_required_keys()
        self.loaded = True

    def add_required_key(self, key, value=None):
        self.required_keys.append(key)

    def _validate_yaml_content(self, c):
        if not isinstance(c, dict):
            raise TypeError(
                u'YAML file {} did not load as a dict.  Please '
                u'check its formatting.'.format(self.config_file_path))

    def _load_yaml(self):
        try:
            with open(self.config_file_path) as f:
                c = yaml.load(f)
                self._validate_yaml_content(c)
                return c
        except IOError:
            return None

    def _validate_key(self, key):
        if not key.isupper():
            raise OrdbokLowercaseKeyException(key, self)

    def _referenced_config_file(self, key, value):
        if not isinstance(value, six.string_types):
            return None
        if not value.startswith(self.config.namespace):
            return None

        referenced_config_files = [k for k in self.config_files_lookup.keys()
                                   if value.startswith(k)]

        if len(referenced_config_files) == 0:
            raise OrdbokMissingConfigFileException(key, self)
        elif len(referenced_config_files) > 1:
            raise OrdbokAmbiguousConfigFileException(referenced_config_files)

        referenced_config_file = referenced_config_files[0]

        if referenced_config_file == self.keyword:
            raise OrdbokSelfReferenceException(key, self)
        elif self.config_files_lookup[referenced_config_file].loaded:
            raise OrdbokPreviouslyLoadedException(
                self.config_files_lookup, referenced_config_file, self)

        return referenced_config_file

    def _validate_nested_keys(self, d):
        for key, value in d.items():
            if isinstance(value, six.string_types):
                if any(True for k in self.config_files_lookup.keys() if
                       value.startswith(k)):
                    raise OrdbokNestedRequiredKeyException(value)
            if isinstance(value, dict):
                self._validate_nested_keys(value)
            pass

    def _process_key_value(self, key, value):
        if isinstance(value, dict):
            pass
        self._validate_key(key)
        if isinstance(value, dict):
            self._validate_nested_keys(value)
        referenced_config_file = self._referenced_config_file(key, value)
        if referenced_config_file:
            self.config_files_lookup[referenced_config_file].add_required_key(
                key, value)
        else:
            self.config[key] = value

    def _load(self):
        if self.envs and self.config['ENVIRONMENT'] not in self.envs:
            return

        c = self._load_yaml()
        if not c:
            return

        c = c.get(self.config['ENVIRONMENT'].upper(), c)

        for key, value in c.items():
            self._process_key_value(key, value)

    def _check_required_keys(self, custom_exception_gen=None):
        for key in self.required_keys:
            if self.config.get(key) is None:
                if custom_exception_gen:
                    raise custom_exception_gen(self, key)
                else:
                    raise OrdbokMissingKeyException(key, self)
