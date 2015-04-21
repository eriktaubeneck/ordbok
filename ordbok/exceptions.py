class OrdbokException(Exception):
    pass


class OrdbokKeyException(OrdbokException):
    def __init__(self, key, config_file):
        self.key = key
        self.config_file_path = config_file.config_file_path


class OrdbokMissingConfigFileException(OrdbokKeyException):
    def __repr__(self):
        return ('{0} is required to be specified in {1} '
                'but {1} was not registered with Ordbok'.format(
                    self.key, self.config_file_path))


class OrdbokLowercaseKeyException(OrdbokKeyException):
    def __repr__(self):
        return '{} config key in {} must be uppercase.'.format(
            self.key, self.config_filename)


class OrdbokMissingKeyException(OrdbokKeyException):
    def __repr__(self):
        return ('{} config key should be specified in {} but was not found.'
                ''.format(self.key, self.config_filename))


class OrdbokSelfReferenceException(OrdbokKeyException):
    def __repr__(self):
        return ('Cannot require {} to be required in its own file ({}).'
                ''.format(self.key, self.config_filename))


class OrdbokAmbiguousConfigFileException(OrdbokException):
    def __init__(self, referenced_config_files):
        self.referenced_config_files = referenced_config_files

    def __repr__(self):
        return ('Config file names are ambiguous. Please make them '
                'distinct: {}'.format(self.referenced_config_files))


class OrdbokPreviouslyLoadedException(OrdbokException):
    def __init__(self, config_files_lookup,
                 referenced_config_file, config_file):
        self.previously_loaded_filename = (
            config_files_lookup[referenced_config_file].filename)
        self.current_filename = config_file.filename

    def __repr__(self):
        return ('Cannot specify {0} required Ordbok config variables in '
                '{1}, {0} is loaded before {1}.'.format(
                    self.previously_loaded_filename, self.current_filename))


class OrdbokNestedRequiredKeyException(OrdbokException):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return ('Cannot specifiy {} required Ordbok config variable '
                'in a nested config dictionary'.format(self.value))


class OrdbokMissingPrivateKeyException(OrdbokException):
    def __repr__(self):
        return ('PRIVATE_KEY_ORDBOK config variable not found. '
                'Please set in configuration loaded before PrivateConfigFile '
                'or in the OS environment as PRIVATE_KEY_ORDBOK.')


class OrdbokTargetedEnvKeyException(OrdbokException):
    def __init__(self, key, env_key):
        self.key = key
        self.env_key = env_key

    def __repr__(self):
        return ('{} config key should be specified in the environment as '
                '{} but was not found.'.format(self.key, self.env_key))


class OrdbokMissingPrivateConfigFile(OrdbokException):
    def __init__(self, config_file):
        self.config_file_path = config_file.config_file_path

    def __repr__(self):
        return ("Private config file '{0}' not found. Please create and run "
                "`ordbok encrypt {0}`.".format(self.config_file_path))


class OrdbokMissingEncryptedPrivateConfigFile(OrdbokMissingPrivateConfigFile):
    def __repr__(self):
        return ("Encrypted version of private config file '{0}' not found. "
                "Please run `ordbok encrypt {0}`.".format(
                    self.config_file_path))
