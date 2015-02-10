import os
import yaml
import sys


def is_str_or_unicode(s):
    if sys.version_info[0] < 3:
        return isinstance(s, basestring)
    else:
        return isinstance(s, str)


class ConfigFile(object):
    def __init__(self, filename, config):
        self.filename = filename
        self.config = config
        self.keyword = '{}_{}'.format(
            self.config.near_miss_key, os.path.splitext(self.filename)[0])
        self.required_keys = []
        self.config_file_path = os.path.join(
            self.config.config_cwd, self.config.config_dir, self.filename)
        self.loaded = False

    def load(self, config_files_lookup):
        self._load(config_files_lookup)
        self._check_required_keys()
        self.loaded = True

    def add_required_key(self, key, value=None):
        self.required_keys.append(key)

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
                config_files = [k for k in config_files_lookup.keys()
                                if value.startswith(k)]
                if len(config_files) == 0:
                    raise Exception(
                        '{0} is required to be specified in {1} '
                        'but {1} was not registered with Ordbok'.format(
                            key, self.config_file_path))
                elif len(config_files) > 1:
                    raise Exception(
                        'Config file names are ambiguous. Please make them '
                        'distinct: {}'.format(config_files)
                    )
                config_file = config_files[0]
                if config_file == self.keyword:
                    raise Exception(
                        'Cannot require {} required Ordbok config '
                        'variables in their own file.'.format(
                            self.filename))
                elif config_files_lookup[config_file].loaded:
                    raise Exception(
                        'Cannot specify {0} required Ordbok config '
                        'variables in {1}, {0} is loaded before '
                        '{1}.'.format(
                            config_files_lookup[config_file].filename,
                            self.filename))
                config_files_lookup[config_file].add_required_key(key, value)
            else:
                self.config[key] = value

    def _check_required_keys(self, custom_exception_gen=None):
        for key in self.required_keys:
            if self.config.get(key) is None:
                if custom_exception_gen:
                    raise custom_exception_gen(self, key)
                else:
                    raise Exception(
                        '{} config key should be specified in {} '
                        'but was not found.'.format(key, self.filename))


class ConfigEnv(ConfigFile):
    def __init__(self, config):
        self.config = config
        self.keyword = '{}_env_config'.format(self.config.near_miss_key)
        self.required_keys = []
        self.keyword_lookup = {}
        self.loaded = False

    def add_required_key(self, key, value):
        if value == self.keyword:
            self.required_keys.append(key)
        elif value.startswith(self.keyword):
            self.keyword_lookup[key] = value.replace(self.keyword+'_', '')
            self.required_keys.append(key)

    def _load(self, _):
        environ = {
            key.replace(self.config.near_miss_key.upper()+'_', ''): value
            for key, value in os.environ.items() if value and
            key.startswith(self.config.near_miss_key.upper())}
        for key, value in environ.items():
            self.config[key] = yaml.load(value)

        for key, env_key in self.keyword_lookup.items():
            value = os.environ.get(env_key.upper(), None)
            if value is None:
                raise Exception(
                    '{} config key should be specified in the environment as '
                    '{} but was not found.'.format(key, env_key))
            self.config[key] = value

    def _check_required_keys(self):
        def custom_exception_gen(_, key):
            return Exception(
                '{} config key should be specified in the environment '
                'but was not found.'.format(key))
        return super(ConfigEnv, self)._check_required_keys(
            custom_exception_gen=custom_exception_gen)


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

        self.config_files = [ConfigFile(f, self) for f
                             in self.custom_config_files]

        if self.include_env:
            self.config_files.append(ConfigEnv(self))

        config_files_lookup = {cf.keyword: cf for cf in self.config_files}
        for config_file in self.config_files:
            config_file.load(config_files_lookup)
