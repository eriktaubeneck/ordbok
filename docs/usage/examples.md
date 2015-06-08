## Examples

### Basic Flask Example
`app/__init__.py`:

```
from ordbok.flask_helper import FlaskOrdbok

ordbok = FlaskOrdbok()

def create_app():
    app = Flask(__name__)
    ordbok.init_app(app)
    ordbok.load()
    app.config.update(ordbok)
    return app

if __name__ == "__main__":
    app = create_app()
    ordbok.app_run(app)

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
