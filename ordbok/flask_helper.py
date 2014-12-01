from . import Ordbok

from flask import Flask as BaseFlask, Config as BaseConfig


class OrdbokFlaskConfig(BaseConfig, Ordbok):
    """
    Extented version of the builtin Flask `Config` that inherits
    a `from_yaml` method from Ordbok so that config varibables
    can be defined there.
    """
    def __init__(self, *args, **kwargs):
        self.set_defaults(**kwargs)
        return super(OrdbokFlaskConfig, self).__init__(*args, **kwargs)

    @property
    def config_cwd(self):
        return self.root_path


def make_config(self, instance_relative=False):
    root_path = self.root_path
    if instance_relative:
        root_path = self.instance_path
    return self.config_class(root_path, self.default_config)


def run(self, *args, **kwargs):
    if self.config_class is not OrdbokFlaskConfig:
        raise Exception(
            'Cannot override Flask.run() without using OrdbokFlaskConfig '
            'as Flask.config_class.')
    if kwargs.get('use_reloader') is not False and self.debug:
        kwargs.setdefault('extra_files', [])
        kwargs['extra_files'].extend(self.config.config_file_names)
    return super(Flask, self).run(*args, **kwargs)


class Flask(BaseFlask):
    """
    Extened version of `Flask` that implements the custom config class
    defined above.
    """
    config_class = OrdbokFlaskConfig
    make_config = make_config
    run = run
