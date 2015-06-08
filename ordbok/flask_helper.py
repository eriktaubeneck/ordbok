from .ordbok import Ordbok


class FlaskOrdbok(Ordbok):
    def __init__(self, app=None, **kwargs):
        if app:
            self.init_app(app)
        return super(FlaskOrdbok, self).__init__(**kwargs)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['ordbok'] = self
        self._root_path = app.config.root_path

    def app_run(self, app, *args, **kwargs):
        if kwargs.get('use_reloader') is not False and app.debug:
            extra_files = kwargs.get('extra_files', [])
            extra_files.extend(self.config_file_names)
            if extra_files:
                kwargs['extra_files'] = extra_files
        return app.run(*args, **kwargs)
