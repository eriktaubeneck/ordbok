import six
from .config_file import ConfigFile


def create_config_file(f):
    if isinstance(f, ConfigFile):
        return f
    elif isinstance(f, six.string_types):
        return ConfigFile(f)
    else:
        raise TypeError(
            'Ordbok.config_files can only be derived from '
            'ordbok.ConfigFile or the filename of a config file')
