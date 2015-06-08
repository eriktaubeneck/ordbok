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


```
from ordbok.flask_helper import FlaskOrdbok

app = Flask(__name__)
ordbok = FlaskOrdbok(app)
ordbok.load()
app.config.update(ordbok)
```
(or similar depending upon your setup).

For your local development app, you can replace

```
app.run()
```

with

```
ordbok.app_run(app)
```

This updated app runner monitors your config files for changes and triggers the reloader when running `app.run()` in debug mode, just like with code changes.
