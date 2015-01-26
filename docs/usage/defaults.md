## Usage

See [Quickstart](../get-started.md#quickstart) for getting initially setup.


### Defaults
Generally when using Ordbok, these following kwargs can be supplied at initialization. However when working with Flask, initialization of the config happens internally, so a helper method `app.config.update_defaults()` is provided. This must be called before `app.config.load()` to have any effect.

  - `config_path` defaults to `config` and looks for files in this directory relative to the current working directory (or the `app.root_dir` in Flask).
  - `custom_config_files` defaults to `['config.yml', 'local_config.yml']`. If you like to change these or add more, specify them as a string of the filename here. As above, earlier files will be overridden by later files.
  - `include_env` defaults to `True`, but if set to `False`, the environment will not be checked by the `config.load()` method.
  - `near_miss_key` is used to avoid conflicts of real configuration values and defaults to `'ordbok'`. (If you override this, you'll want to avoid using something like `'flask'` or `'app'`.)
  - `default_environment` defaults to `development`. If `config['ENVIRONMENT']` is unset, we look in the environment for `ORDBOK_ENVIRONMENT`. If this is unset, the `default_environment` is used.
