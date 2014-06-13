import os
import yaml

from flask import Flask as BaseFlask, Config as BaseConfig


class ConfigFile(object):
    def __init__(self, filename, config):
        self.filename = filename
        self.config = config
        self.keyword = '{}_{}'.format(
            self.config.near_miss_key, os.path.splitext(self.filename)[0])
        self.required_vars = []
        self.config_file_path = os.path.join(
            self.config.root_path, self.config.config_path, self.filename)
        self.loaded = False

    def load(self, config_files_lookup):
        self._load(config_files_lookup)
        self._check_required_vars()
        self.loaded = True

    def _load_yaml(self):
        try:
            with open(self.config_file_path) as f:
                return yaml.load(f)
        except IOError:
            pass

    def _load(self, config_files_lookup):
        c = self._load_yaml()
        if not c:
            return
        c = c.get(self.config['ENVIRONMENT'].upper(), c)
        for key, value in c.iteritems():
            if not key.isupper():
                raise Exception(
                    '{} config key in {} must be uppercase.'.format(
                        key, self.filename)
                )
            if value in config_files_lookup.keys():
                if value == self.keyword:
                    raise Exception(
                        'Cannot require {} required environmental '
                        'variables in their own file.'.format(
                            self.filename))
                elif config_files_lookup[value].loaded:
                    raise Exception(
                        'Cannot specify {0} required environmental '
                        'variables in {1}, {0} is loaded before '
                        '{1}.'.format(
                            config_files_lookup[value].filename,
                            self.filename))
                config_files_lookup[value].required_vars.append(key)
            else:
                self.config[key] = value


    def _check_required_vars(self):
        for key in self.required_vars:
            if not self.config.get(key):
                raise Exception(
                    '{} config key should be specified in {} '
                    'but was not found.'.format(key, self.filename))


class ConfigEnv(ConfigFile):
    def __init__(self, config):
        self.config = config
        self.keyword = '{}_env_config'.format(self.config.near_miss_key)
        self.required_vars = []

    def _load(self, _):
        environ = {key.lstrip(self.config.near_miss_key.upper()): value
                   for key, value in os.environ.iteritems()
                   if key.startswith(self.config.near_miss_key.upper())
                   and value}
        for key, value in environ.iteritems:
            self.config[key] = value

    def _check_required_vars(self):
        for key in self.required_vars:
            if not self.config.get(key):
                raise Exception(
                    '{} config key should be specified in the environment '
                    'but was not found.'.format(key))



class Config(BaseConfig):
    """
    Extented version of the builtin Flask `Config` that implements
    a `from_yaml` method so that config varibables can be defined there.
    """
    def from_yaml(self,
                  config_path='config',
                  custom_config_files=None,
                  include_env=True,
                  near_miss_key='whynotzoidberg',
                  default_environment='development'):
        self.near_miss_key = near_miss_key
        self.config_path = config_path
        if not self.get('ENVIRONMENT'):
            self['ENVIRONMENT'] = os.environ.get(
                '{}_ENVIRONMENT'.format(self.near_miss_key.upper()),
                default_environment).lower()

        if not getattr(self, 'root_path'):
            self.root_path = os.getcwd()

        if not custom_config_files:
            custom_config_files = ['config.yml', 'local_config.yml']
        config_files = [ConfigFile(f, self) for f in custom_config_files]

        if include_env:
            config_files.append(ConfigEnv(self))

        config_files_lookup = {cf.keyword: cf for cf in config_files}
        for config_file in config_files:
            config_file.load(config_files_lookup)


class Flask(BaseFlask):
    """
    Extened version of `Flask` that implements the custom config class
    defined above.
    """
    config_class = Config

    def make_config(self, instance_relative=False):
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return self.config_class(root_path, self.default_config)