# Installation

Inside a [virtualenv](http://virtualenv.readthedocs.org/en/latest/) run

```
pip install ordbok
```

# Quickstart

```
from ordbok import Ordbok
config = Ordbok()
config.load()
```

Then, in your app root path, create a directory `config` and add two files `config.yml` and `local_config.yml`. See [Usage](#usage) for more detailed usage and [Example](#examples) for an example YAML configuration.

# Quickstart with Flask

In the file in which you initialize your `Flask` object, replace

```
from flask import Flask
```

with

```
from ordbok.flask_helper import Flask
```

and update

```
app = Flask(__name__)
```

to

```
app = Flask(__name__)
app.config.load()
```
(or similar depending upon your setup).

Then, in your app root path, create a directory `config` and add two files `config.yml` and `local_config.yml`. See [Usage](#usage) for more detailed usage and [Example](#examples) for an example YAML configuration.

This updated version of `Flask` also monitors your config files for changes and triggers the reloader when running `app.run()` in debug mode.

The `Flask` object here is whatever version you have install locally (`ordbok.flask_helper` imports `Flask` directly). Regardless, importing `Flask` from `ordbok` does feel a little weird, and if you prefer, you can installed do something to the effect of:

```
from flask import Flask
from ordbok.flask_helper import OrdbokFlaskConfig, make_config, run
Flask.config_class = OrdbokFlaskConfig
Flask.make_config = make_config
Flask.run = run
app = Flask(__name__)
app.config.load()
```

If you look at `ordbok.flask_helper`, this is all that happens to the `Flask` object that's importable. It's very importand that `Flask.make_config` is overridden before the `app` is initialized as `make_config` is called from the initializer.
