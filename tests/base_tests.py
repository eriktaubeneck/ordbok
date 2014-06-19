import os
import unittest
import mock
import fudge
from contextlib import contextmanager
from StringIO import StringIO

from ordbok import Ordbok
from ordbok.flask_helper import Flask, OrdbokFlaskConfig

fudged_config_files = {
    'config.yml': """
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
""",
    'local_config.yml': """
SQLALCHEMY_DATABASE_URL: 'sqlite:///tmp/database.db'
SQLALCHEMY_ECHO: True
""",
    'copied_local_settings_config.yml': """
SQLALCHEMY_DATABASE_URL = 'sqlite:///tmp/database.db'
SQLALCHEMY_ECHO = True
""",
    'bad_yaml_local_settings_config.yml': """
SQLALCHEMY_DATABASE_URL: 'sqlite:///tmp/database.db'
SQLALCHEMY_ECHO = True
"""
}

fudged_config_no_local_file = {
    key: value for key, value in fudged_config_files.iteritems()
    if key == 'config.yml'
}

fudged_config_copied_local_settings = {
    key: value for key, value in fudged_config_files.iteritems()
    if key in ('config.yml', 'copied_local_settings.yml')
}

fudged_config_bad_yaml_local_settings = {
    key: value for key, value in fudged_config_files.iteritems()
    if key in ('config.yml', 'bad_yaml_local_settings.yml')
}

patched_environ = {
    'ORDBOK_ENVIRONMENT': 'production',
    'ORDBOK_SECRET_KEY': '7a1fa63d-f33a-11e3-aab5-b88d12179d58'
}

def fake_file_factory(fudged_config_files):
    @contextmanager
    def fake_file(filename):
        content = fudged_config_files.get(
            os.path.relpath(
                filename,
                os.path.join(os.getcwd(), 'config')),
            '')

        yield StringIO(content)
    return fake_file

class OrdbokTestCase(unittest.TestCase):
    def setUp(self):
        self.ordbok = Ordbok()

    @fudge.patch('__builtin__.open')
    def test_ordbok_default(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        self.ordbok.load()
        self.assertEquals(self.ordbok['ENVIRONMENT'], 'development')
        self.assertEquals(self.ordbok['SECRET_KEY'], 'keep out!')
        self.assertTrue(self.ordbok['DEBUG'])
        self.assertEquals(self.ordbok['SQLALCHEMY_DATABASE_URL'],
                          'sqlite:///tmp/database.db')
        self.assertTrue(self.ordbok['SQLALCHEMY_ECHO'])

    @fudge.patch('__builtin__.open')
    @mock.patch.dict('os.environ', patched_environ)
    def test_ordbok_env(self, fudged_open):
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_no_local_file))
        self.ordbok.load()
        self.assertEquals(self.ordbok['ENVIRONMENT'], 'production')
        self.assertEquals(self.ordbok['SECRET_KEY'],
                          '7a1fa63d-f33a-11e3-aab5-b88d12179d58')
        self.assertFalse(self.ordbok['DEBUG'])
        self.assertEquals(self.ordbok['SQLALCHEMY_DATABASE_URL'],
                          'postgres://user:password@localhost:5432/database')
        self.assertFalse(self.ordbok.get('SQLALCHEMY_ECHO'))

    @unittest.skip('TODO')
    @fudge.patch('__builtin__.open')
    def test_ordbok_copied_local_settings(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(
            fudged_config_copied_local_settings))
        with self.assertRaises(TypeError):
            self.ordbok.load(custom_config_files=[
                'config.yml', 'copied_local_settings_config.yml'])

    @unittest.skip('TODO')
    @fudge.patch('__builtin__.open')
    def test_ordbok_bad_yaml_local_settings(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(
            fudged_config_copied_local_settings))
        with self.assertRaises(TypeError):
            self.ordbok.load(custom_config_files=[
                'config.yml', 'bad_yaml_local_settings_config.yml'])

    def test_flask_helper(self):
        app = Flask(__name__)
        self.assertIsInstance(app.config, OrdbokFlaskConfig)
