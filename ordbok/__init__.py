import os
import yaml
import sys


def is_str_or_unicode(s):
    if sys.version < '3':
        return isinstance(s, basestring)
    else:
        return isinstance(s, str)


class ConfigFile(object):
    def __init__(self, filename, config):
        self.filename = filename
        self.config = config
        self.keyword = '{}_{}'.format(
            self.config.near_miss_key, os.path.splitext(self.filename)[0])
        self.required_vars = []
        self.config_file_path = os.path.join(
            self.config.config_cwd, self.config.config_dir, self.filename)
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
        for key, value in c.items():
            if not key.isupper():
                raise Exception(
                    '{} config key in {} must be uppercase.'.format(
                        key, self.filename)
                )
            if (is_str_or_unicode(value) and
                    value.startswith(self.config.near_miss_key)):
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
                   for key, value in os.environ.items()
                   if key.startswith(self.config.near_miss_key.upper())
                   and value}
        for key, value in environ.items():
            self.config[key] = yaml.load(value)

    def _check_required_vars(self):
        for key in self.required_vars:
            if not self.config.get(key):
                raise Exception(
                    '{} config key should be specified in the environment '
                    'but was not found.'.format(key))


class Ordbok(dict):
    def __init__(self, **kwargs):
        self.set_defaults(**kwargs)
        return super(Ordbok, self).__init__(**kwargs)

    def set_defaults(self, **kwargs):
        self.custom_config_files = ['config.yml', 'local_config.yml']
        self.update_defaults(
            config_dir=kwargs.get('config_dir', 'config'),
            custom_config_files=kwargs.get('custom_config_files'),
            include_env=kwargs.get('include_env', True),
            near_miss_key=kwargs.get('near_miss_key', 'ordbok'),
            default_environment=kwargs.get('default_environment', 'development')
        )

    def update_defaults(self, **kwargs):
        self.config_dir = kwargs.get('config_dir') or self.config_dir
        self.custom_config_files = (kwargs.get('custom_config_files') or
                                    self.custom_config_files)
        self.include_env = kwargs.get('include_env') or self.include_env
        self.near_miss_key = kwargs.get('near_miss_key') or self.near_miss
        self.default_environment = (kwargs.get('default_environment') or
                                    self.default_environment)

    @property
    def config_cwd(self):
        return os.getcwd()

    def load(self):
        if not self.get('ENVIRONMENT'):
            self['ENVIRONMENT'] = os.environ.get(
                '{}_ENVIRONMENT'.format(self.near_miss_key.upper()),
                self.default_environment).lower()

        config_files = [ConfigFile(f, self) for f in self.custom_config_files]

        if self.include_env:
            config_files.append(ConfigEnv(self))

        config_files_lookup = {cf.keyword: cf for cf in config_files}
        for config_file in config_files:
            config_file.load(config_files_lookup)
