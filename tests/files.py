import os
from contextlib import contextmanager
from io import StringIO, BytesIO

open_function_string = 'ordbok.open_wrapper'

fudged_config_files = {
    u'config.yml': u"""
COMMON: &common
  SECRET_KEY: 'keep out!'
  DEBUG: False

DEVELOPMENT: &development
  <<: *common
  DEBUG: True
  SQLALCHEMY_DATABASE_URL: 'ordbok_local_config'
  TEST_BOOLEAN_VAR: 'ordbok_local_config'

PRODUCTION:
  <<: *common
  SECRET_KEY: 'ordbok_env_config'
  SQLALCHEMY_DATABASE_URL: 'postgres://user:password@localhost:5432/database'
""",
    u'local_config.yml': u"""
SQLALCHEMY_DATABASE_URL: 'sqlite:///tmp/database.db'
SQLALCHEMY_ECHO: True
TEST_BOOLEAN_VAR: False
""", }

fudged_config_no_local_file = {
    key: value for key, value in fudged_config_files.items()
    if key == u'config.yml'
}

patched_environ = {
    u'ORDBOK_ENVIRONMENT': u'production',
    u'ORDBOK_SECRET_KEY': u'7a1fa63d-f33a-11e3-aab5-b88d12179d58',
    u'ORDBOK_TEST_BOOLEAN': u'True',
    u'ORDBOK_TEST_INT': u'42',
    u'REDISCLOUD_URL': u'why-not-zoidberg?',
}


def fake_file_factory(fudged_config_files):
    @contextmanager
    def fake_file(filename, mode='r'):
        content = fudged_config_files.get(
            os.path.relpath(
                filename,
                os.path.join(os.getcwd(), 'config')),
            None)
        if content is None:
            raise IOError('{} not found'.format(filename))
        if isinstance(content, bytes):
            yield BytesIO(content)
        else:
            yield StringIO(content)
    return fake_file
