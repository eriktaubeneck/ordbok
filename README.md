# Ordbok

[![Build Status](https://travis-ci.org/alphaworksinc/ordbok.svg?branch=master)](https://travis-ci.org/alphaworksinc/ordbok)
[![Coverage Status](https://coveralls.io/repos/alphaworksinc/ordbok/badge.png?branch=master)](https://coveralls.io/r/alphaworksinc/ordbok?branch=master)
[![Latest Version](https://pypip.in/version/ordbok/badge.png)](https://pypi.python.org/pypi/ordbok/)
[![Downloads](https://pypip.in/download/ordbok/badge.png)](https://pypi.python.org/pypi/ordbok/)
[![License](https://pypip.in/license/ordbok/badge.png)](https://pypi.python.org/pypi/ordbok/)

As your application grows, configuration can get a bit chaotic, especially if you have multiple versions (local, deployed, staging, etc.) Ordbok brings order to that chaos.

Ordbok abstracts the loading of a configuration from YAML files into a Python dictionary, and also has a specific setup for use with Flask. See [TODO](#todo) for plans to expand this.

![Svenska Akademiens ordbok](http://fc01.deviantart.net/fs70/i/2011/048/b/1/svenska_akademiens_ordbok_by_droemmaskin-d39rta7.jpg)
_<a href="http://droemmaskin.deviantart.com/art/Svenska-Akademiens-ordbok-197812735">Svenska Akademiens ordbok</a> by <span class="username-with-symbol u"><a class="u regular username" href="http://droemmaskin.deviantart.com/">droemmaskin</a><span class="user-symbol regular" data-quicktip-text="" data-show-tooltip="" data-gruser-type="regular"></span></span> on <a href="http://www.deviantart.com">deviantART</a>. Provided under [Attribution-NonCommercial-ShareAlike 3.0 Unported](http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode)_



## Installation

Inside a [virtualenv](http://virtualenv.readthedocs.org/en/latest/) run

```
pip install ordbok
```

## Quickstart

```
from ordbok import Ordbok
config = Ordbok()
config.load()
```

Then, in your app root path, create a directory `config` and add two files `config.yml` and `local_config.yml`. See [Usage](#usage) for more detailed usage and [Example](#examples) for an example YAML configuration.

## Quickstart with Flask

In the file in which you initialize your `Flask` object, replace

```from flask import Flask```

with

```from ordbok.flask_helper import Flask```

and update

```app = Flask(__name__)```

to

```
app = Flask(__name__)
app.config.load()
```
(or similar depending upon your setup).

Then, in your app root path, create a directory `config` and add two files `config.yml` and `local_config.yml`. See [Usage](#usage) for more detailed usage and [Example](#examples) for an example YAML configuration.

The `Flask` object here is whatever version you have install locally (`ordbok.flask_helper` imports `Flask` directly). Regardless, importing `Flask` from `ordbok` does feel a little weird, and if you prefer, you can installed do something to the effect of:

```
from flask import Flask
from ordbok.flask_helper import OrdbokFlaskConfig, make_config
Flask.config_class = OrdbokFlaskConfig
Flask.make_config = make_config
app = Flask(__name__)
app.config.load()
```

If you look at `ordbok.flask_helper`, this is all that happens to the `Flask` object that's importable. It's very importand that `Flask.make_config` is overridden before the `app` is initialized as `make_config` is called from the initializer.

## Usage

See [Quickstart](#quickstart) for getting initially setup.

### Hierarchical Config Files

#### YAML Config Files
As your Flask application grows, you may find that your configuration is coming from all over the place, and it may be difficult to understand what is overriding what. Ordbok adds a strict order of operations as to how the config should be loaded, and tools to specify that a certain variable should be specified later in the chain.

The default configurations has three configuration steps:
  1. `config.yml`
  2. `local_config.yml`
  3. Environmental Variables

YAML already has some structure like this, but the idea behind the `local_config.yml` is for settings that may be dependent of a developers own configuration.

Variables that show up in multiple files will assume the value in the later declaration. Moreover, variables can be declared in earlier files such that they must be found in later file or the environment. This works with the `<near_miss_key>`, which defaults to `ordbok` but can be specified. For example setting `KEY: 'ordbok_local_config'` in `config.yml` will raise an exception if `KEY` isn't specified in `local_config.yml`.

####OS Environmental Config
Config variables can be loaded from the OS environment just like the YAML config files, and is the last in the hierarchy of config variables sources. Config variables are loaded from the OS environment in two ways:

1. Every environmental variable of the form `ORDBOK_<KEY>` will be loaded into the Ordbok config dict as `'<KEY>':value` (where `value` is the value of the environmental variable.)

2. In any YAML config file, setting `KEY: ordbok_env_conifg_<env_var>` will look for `<ENV_VAR>` in the OS Environment and load the value into the Ordbok config dict as `'KEY': value`.

Specifying `KEY: 'ordbok_env_config'` or `KEY: 'ordbok_env_config_<env_var>'` in any of the YAML config files will raise an exception if `ORDBOK_KEY` isn't specified in the environment.

NOTE: OS Environment variables and Ordbok config dict keys are assumed to be uppercase (`ENV_VAR` and `'KEY'` respectively), even if the value is specified in lowercase (`env_var`.)

### Defaults
Generally when using Ordbok, these following kwargs can be supplied at initialization. However when working with Flask, initialization of the config happens internally, so a helper method `app.config.update_defaults()` is provided. This must be called before `app.config.load()` to have any effect.

  - `config_path` defaults to `config` and looks for files in this directory relative to the current working directory (or the `app.root_dir` in Flask).
  - `custom_config_files` defaults to `['config.yml', 'local_config.yml']`. If you like to change these or add more, specify them as a string of the filename here. As above, earlier files will be overridden by later files.
  - `include_env` defaults to `True`, but if set to `False`, the environment will not be checked by the `config.load()` method.
  - `near_miss_key` is used to avoid conflicts of real configuration values and defaults to `'ordbok'`. (If you override this, you'll want to avoid using something like `'flask'` or `'app'`.)
  - `default_environment` defaults to `development`. If `config['ENVIRONMENT']` is unset, we look in the environment for `ORDBOK_ENVIRONMENT`. If this is unset, the `default_environment` is used.

## Examples

### Basic Flask Example
`app/__init__.py`:

```
from ordbok.flask_helper import Flask

def create_app():
    app = Flask(__name__)
    app.config.load()
    return app

if __name__ == "__main__":
    app = create_app()

```
`app/config/config.yml`:

```
COMMON: &common
  SECRET_KEY: 'keep out!'
  DEBUG: False

DEVELOPMENT: &development
  <<: *common
  DEBUG: True
  SQLALCHEMY_DATABASE_URL: 'ordbok_local_config'

PRODUCTION:
  <<: *common
  SECRET_KEY: 'ordbok_env_config'
  SQLALCHEMY_DATABASE_URL: 'postgres://user:password@localhost:5432/database'

```

`app/config/local_config.yml`:

```
SQLALCHEMY_DATABASE_URL: 'sqlite:///tmp/database.db'
SQLALCHEMY_ECHO: True
```

ran with `python app/__init__.py` will run a Flask app with the following configuration*:

```
{ENVIRONMENT: 'development',
 SECRET_KEY: 'keep out!',
 DEBUG: True,
 SQLALCHEMY_DATABASE_URL: 'sqlite:///tmp/database.db',
 SQLALCHEMY_ECHO: True}

```

and ran with (in bash):

```
export ORDBOK_ENVIRONMENT=PRODUCTION
export ORDBOK_SECRET_KEY=7a1fa63d-f33a-11e3-aab5-b88d12179d58
python app/__init__.py
```

will run a Flask app with the following configuration*:

```
{ENVIRONMENT: 'production',
 SECRET_KEY: '7a1fa63d-f33a-11e3-aab5-b88d12179d58',
 DEBUG: False,
 SQLALCHEMY_DATABASE_URL: 'postgres://user:password@localhost:5432/database'}

```
*Note: These are not complete configurations; Flask adds a set of defaults on it's own. These only represent the values set from the config files and the environment.

By setting `SQLALCHEMY_DATABASE_URL: 'ordbok_local_config'` and `SECRET_KEY: 'ordbok_env'` in our `config/config.yml` file, we would raise an exception if those values were not found in `config/local_config.yml` and the environment, respectively.


## TODO

 - Add advanced Example to README.md
 - Add support for more file types (JSON, maybe XML?)
 - Add integrated support for other frameworks (Pyramid, Django, etc.)
 - Add a private config file type, where an encrypted version of the file could exist in the repo, and a password could be set in the environment where the private keys are used. Will require integration with Flask-Script to provide methods to decrypt locally with the password, edit keys, and re-encrypt.


## Contributing

If anything on the TODO list looks like something you'd like to take on, go
ahead and fork the project and submit a Pull Request. For other features,
please first open an issue proposing the feature/change.

### Environment

To hack on ordbok, make sure to install the development requirements in your
virtual environment.

`pip install -r dev_requirements.txt`

### Tests

Pull Requests should include tests covering the changes/features being
proposed.  To run the test suite, simply run:

`nosetests`

#LICENSE
MIT License

Copyright (C) 2014 by Alphaworks Inc., Erik Taubeneck

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
