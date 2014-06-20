import os
import yaml


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

        if not isinstance(c, dict):
            raise TypeError(u'YAML file {} did not load as a dict.  Please '
                            u'check its formatting.'.format(
                                self.config_file_path))

        c = c.get(self.config['ENVIRONMENT'].upper(), c)
        for key, value in c.iteritems():
            if not key.isupper():
                raise Exception(
                    '{} config key in {} must be uppercase.'.format(
                        key, self.filename)
                )
            if isinstance(value, basestring) and value.startswith('ordbok'):
                if value not in config_files_lookup.keys():
                    raise Exception(
                        '{0} is required to be specified in {1} '
                        'but {1} was not registered with Ordbok'.format(
                            key, self.config_file_path))
                elif value == self.keyword:
                    raise Exception(
                        'Cannot require {} required Ordbok config '
                        'variables in their own file.'.format(
                            self.filename))
                elif config_files_lookup[value].loaded:
                    raise Exception(
                        'Cannot specify {0} required Ordbok config '
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
        self.loaded = False

    def _load(self, _):
        environ = {key.lstrip(self.config.near_miss_key.upper()+'_'): value
                   for key, value in os.environ.iteritems()
                   if key.startswith(self.config.near_miss_key.upper())
                   and value}
        for key, value in environ.iteritems():
            self.config[key] = yaml.load(value)

    def _check_required_vars(self):
        for key in self.required_vars:
            if not self.config.get(key):
                raise Exception(
                    '{} config key should be specified in the environment '
                    'but was not found.'.format(key))


class Ordbok(dict):
    def load(self,
             config_path='config',
             custom_config_files=None,
             include_env=True,
             near_miss_key='ordbok',
             default_environment='development'):
        self.near_miss_key = near_miss_key
        self.config_path = config_path
        if not self.get('ENVIRONMENT'):
            self['ENVIRONMENT'] = os.environ.get(
                '{}_ENVIRONMENT'.format(self.near_miss_key.upper()),
                default_environment).lower()

        if not getattr(self, 'root_path', None):
            self.root_path = os.getcwd()

        if not custom_config_files:
            custom_config_files = ['config.yml', 'local_config.yml']
        config_files = [ConfigFile(f, self) for f in custom_config_files]

        if include_env:
            config_files.append(ConfigEnv(self))

        config_files_lookup = {cf.keyword: cf for cf in config_files}
        for config_file in config_files:
            config_file.load(config_files_lookup)
