class OrdbokException(Exception):
    pass


class OrdbokMissingConfigFileException(OrdbokException):
    def __init__(self, key, config_file):
        self.key = key
        self.config_file_path = config_file.config_file_path

    def __repr__(self):
        return ('{0} is required to be specified in {1} '
                'but {1} was not registered with Ordbok'.format(
                    self.key, self.config_file_path))


class OrdbokAmbiguousConfigFileException(OrdbokException):
    def __init__(self, referenced_config_files):
        self.referenced_config_Files

    def __repr__(self):
        return ('Config file names are ambiguous. Please make them '
                'distinct: {}'.format(self.referenced_config_files))


class OrdbokSelfReferenceException(OrdbokException):
    def __init__(self, config_file):
        self.config_filename = config_file.filename

    def __repr__(self):
        return ('Cannot require {} required Ordbok config variables '
                'in their own file.'.format(self.config_filename))


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


class OrdbokLowercaseKeyException(OrdbokException):
    def __init__(self, key, config_file):
        self.key = key
        self.config_filename = config_file.filename

    def __repr__(self):
        return '{} config key in {} must be uppercase.'.format(
            self.key, self.config_filename)


class OrdbokNestedRequiredKeyException(OrdbokException):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return ('Cannot specifiy {} required Ordbok config variable '
                'in a nested config dictionary'.format(self.value))


class OrdbokMissingKeyException(OrdbokException):
    def __init__(self, key, config_file):
        self.key = key
        self.config_filename = config_file.filename

    def __repr__(self):
        return ('{} config key should be specified in {} but was not found.'
                ''.format(self.key, self.config_filename))
