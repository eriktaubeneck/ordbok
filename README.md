# Flask-YAML-Config

As your application grows, configuration can get a bit chaotic, especially if you have multiple versions (local, deployed, staging, etc.) Flask-YAML-Config brings order to that chaos.

## Installation

Inside a [virtualenv](http://virtualenv.readthedocs.org/en/latest/) run

```
pip install flask-yaml-config
```

## Quickstart

In the file in which you initialize your `Flask` object, replace

```from flask import Flask```

with

```from flask.ext.yaml_config import Flask```

and update

```app = Flask(__name__)```

to

```
app = Flask(__name__)
app.config.from_yaml()
```
(or similar depending upon your setup).

Then, in your app root path, create a directory `config` and add two files `config.yml` and `local_config.yml`. See [Usage](#usage) for more detailed usage and [Example](#examples) for an example YAML configuration.

## Usage

See [Quickstart](#quickstart) for getting initially setup.

### Hierarchical Config Files

#### YAML Config Files
As your Flask application grows, you may find that your configuration is coming from all over the place, and it may be difficult to understand what is overriding what. Flask-Yaml-Config adds a strict order of operations as to how the config should be loaded, and tools to specify that a certain variable should be specified later in the chain.

The default configurations has three configuration steps:
  1. `config.yml`
  2. `local_config.yml`
  3. Environmental Variables

YAML already has some structure like this, but the idea behind the `local_config.yml` is for settings that may be dependent of a developers own configuration.

Variables that show up in multiple files will assume the value in the later declaration. Moreover, variables can be declared in earlier files such that they must be found in later file or the environment. This works with the `<near_miss_key>`, for example setting `KEY: '<near_miss_key>_local_config'` in `config.yml` will raise an exception if `KEY` isn't specified in `local_config.yml`.

####Environmental Config
The environment works mostly like the YAML config files, and is the last in the hierarchy chain of loading config variables. We take every environmental variable of the form `<NEAR_MISS_KEY>_KEY` in the environment (where `<NEAR_MISS_KEY>` is the uppercase of `<near_miss_key>`), and add it to the Flask config. Similar to the files, setting `KEY: '<near_miss_key>_env'` in any of the YAML config files will raise an exception if `<NEAR_MISS_KEY>_KEY` isn't specified in the environment.


### Defaults
These are all optional kwargs that can be use with `app.config.from_yaml(**kwargs)`.

  - `config_path` defaults to `config` and looks for files in this directory relative to the `app.root_dir`.
  - `custom_config_files` defaults to `['config.yml', 'local_config.yml']`. If you like to change these or add more, specify them as a string of the filename here. As above, earlier files will be overridden by later files.
  - `include_env` defaults to `True`, but if set to `False`, the environment will not be checked by the `config.from_yaml()` method.
  - `near_miss_key` is used to avoid conflicts of real configuration values and defaults to `'whynotzoidberg'`. (You'll likely want to override this if you're not a ravid Futurama fan. However, you probably don't want to set this to `'flask'` or `'app'`.)
  - `default_environment` defaults to `development`. If `config['ENVIRONMENT']` is unset, we look in the environment for `<NEAR_MISS_KEY>_ENVIRONMENT` (where `<NEAR_MISS_KEY>` is the uppercase of your `near_miss_key`.) If this is unset, the `default_environment` is used.

## Examples

### Basic Example
`app/__init__.py`:

```
from flask.ext.flask_yaml_config import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_yaml()
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
  SQLALCHEMY_DATABASE_URL: 'whynotzoidberg_local_config'

PRODUCTION:
  <<: *common
  SECRET_KEY: 'whynotzoidberg_env'
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
export WHYNOTZOIDBERG_ENVIRONMENT=PRODUCTION
export WHYNOTZOIDBERG_SECRET_KEY=7a1fa63d-f33a-11e3-aab5-b88d12179d58
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

By setting `SQLALCHEMY_DATABASE_URL: 'whynotzoidberg_local_config'` and `SECRET_KEY: 'whynotzoidberg_env'` in our `config/config.yml` file, we would raise an exception if those values were not found in `config/local_config.yml` and the environment, respectively.


## TODO

 - Add advanced Example to README.md
 - Add ability to specify where to look in environment for a variable (e.g. you want to look for `KEY` at `HEROKU_PROVIDED_VALUE` rather than `<NEAR_MISS_KEY>_KEY` in the environment.
 - Add a private config file type, where an encrypted version of the file could exist in the repo, and a password could be set in the environment where the private keys are used. Will require integration with Flask-Script to provide methods to decrypt locally with the password, edit keys, and re-encrypt.


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