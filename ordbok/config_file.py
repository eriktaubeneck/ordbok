import os
import yaml
import six


class ConfigFile(object):
    def __init__(self, filename, config=None):
        self.filename = filename
        if config:
            self.init_config(config)

    def init_config(self, config):
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
            if (isinstance(value, six.string_types) and
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
