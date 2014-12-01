import sys
import os
import unittest
import mock
import fudge
from copy import deepcopy
from yaml.scanner import ScannerError
from contextlib import contextmanager
from io import StringIO

from flask import Flask as BaseFlask
from ordbok import Ordbok
from ordbok.flask_helper import (
    Flask as OrdbokFlask, OrdbokFlaskConfig, make_config, run)


if sys.version_info[0] < 3:
    open_function_string = '__builtin__.open'
else:
    open_function_string = 'builtins.open'

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
"""}

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
    def fake_file(filename):
        content = fudged_config_files.get(
            os.path.relpath(
                filename,
                os.path.join(os.getcwd(), 'config')),
            u'')

        yield StringIO(content)
    return fake_file


class OrdbokTestCase(unittest.TestCase):
    def setUp(self):
        self.ordbok = Ordbok()

    @fudge.patch(open_function_string)
    def test_ordbok_default(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        self.ordbok.load()
        self.assertEquals(self.ordbok['ENVIRONMENT'], 'development')
        self.assertEquals(self.ordbok['SECRET_KEY'], 'keep out!')
        self.assertTrue(self.ordbok['DEBUG'])
        self.assertEquals(self.ordbok['SQLALCHEMY_DATABASE_URL'],
                          'sqlite:///tmp/database.db')
        self.assertTrue(self.ordbok['SQLALCHEMY_ECHO'])

    @fudge.patch(open_function_string)
    @mock.patch.dict('os.environ', patched_environ)
    def test_ordbok_env(self, fudged_open):
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_no_local_file))
        self.ordbok.load()
        self.assertEquals(self.ordbok['ENVIRONMENT'], 'production')
        self.assertEquals(self.ordbok['SECRET_KEY'],
                          '7a1fa63d-f33a-11e3-aab5-b88d12179d58')
        self.assertEquals(self.ordbok['TEST_BOOLEAN'], True)
        self.assertEquals(self.ordbok['TEST_INT'], 42)
        self.assertFalse(self.ordbok['DEBUG'])
        self.assertEquals(self.ordbok['SQLALCHEMY_DATABASE_URL'],
                          'postgres://user:password@localhost:5432/database')
        self.assertFalse(self.ordbok.get('SQLALCHEMY_ECHO'))
        self.assertIsNone(self.ordbok.get('REDIS_URL'))

    @fudge.patch(open_function_string)
    @mock.patch.dict('os.environ', patched_environ)
    def test_ordbok_env_reference(self, fudged_open):
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'config.yml': u"""
            REDIS_URL: 'ordbok_env_config_rediscloud_url'
            """})
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_copy))
        self.ordbok.load()
        self.assertEquals(self.ordbok['REDIS_URL'], 'why-not-zoidberg?')

    @fudge.patch(open_function_string)
    def test_ordbok_find_in_local(self, fudged_open):
        '''
        Test that Ordbok raises an Exception when a value is set to be found
        in the local_config.yml file, but the local_config.yml doesn't have the
        value.
        '''
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_no_local_file))
        with self.assertRaises(Exception):
            self.ordbok.load()

    @fudge.patch(open_function_string)
    def test_ordbok_copied_local_settings(self, fudged_open):
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'local_config.yml': u"""
            SQLALCHEMY_DATABASE_URL = 'sqlite:///tmp/database.db'
            SQLALCHEMY_ECHO = True
            """})
        fudged_open.is_callable().calls(fake_file_factory(
            fudged_config_files_copy))
        with self.assertRaises(TypeError):
            self.ordbok.load()

    @fudge.patch(open_function_string)
    def test_ordbok_bad_yaml_local_settings(self, fudged_open):
        fudged_bad_yaml_config_files = deepcopy(fudged_config_files)
        fudged_bad_yaml_config_files.update({
            u'local_config.yml': u"""
            SQLALCHEMY_DATABASE_URL: 'sqlite:///tmp/database.db'
            SQLALCHEMY_ECHO = True
            """
        })
        fudged_open.is_callable().calls(fake_file_factory(
            fudged_bad_yaml_config_files))
        with self.assertRaises(ScannerError):
            self.ordbok.load()


class FlaskOrdbokTestCase(OrdbokTestCase):
    def setUp(self):
        self.app = OrdbokFlask(__name__)
        self.ordbok = self.app.config
        self.ordbok.root_path = os.getcwd()  # the fudged files are here

    def test_flask_helper(self):
        self.assertIsInstance(self.app.config, OrdbokFlaskConfig)

    def test_flask_reloader(self):
        BaseFlask.run = mock.MagicMock(return_value=True)
        self.ordbok.load()
        self.app.debug = True
        self.app.run()
        BaseFlask.run.assert_called()
        BaseFlask.run.assert_called_with(
            extra_files=self.ordbok.config_file_names)

    def test_flask_reloader_debug_off(self):
        BaseFlask.run = mock.MagicMock(return_value=True)
        self.ordbok.load()
        self.app.run()
        BaseFlask.run.assert_called()
        BaseFlask.run.assert_called_with()  # no extra files

    def test_flask_reloader_use_reloader_false(self):
        BaseFlask.run = mock.MagicMock(return_value=True)
        self.ordbok.load()
        self.app.run(use_reloader=False)
        BaseFlask.run.assert_called()
        BaseFlask.run.assert_called_with(use_reloader=False)  # no extra files


class SpecialFlaskOrbokTestCase(unittest.TestCase):
    def setUp(self):
        self.app = OrdbokFlask(__name__)
        self.ordbok = self.app.config

    def test_root_path(self):
        """
        Generally this should be True, however in the above tests
        the way open() was monkey patched required us to override
        this for the the tests.
        """
        self.assertEquals(self.app.root_path, self.ordbok.config_cwd)


class BaseFlaskOrdbokTestCase(unittest.TestCase):
    def setUp(self):
        BaseFlask.config_class = OrdbokFlaskConfig
        BaseFlask.make_config = make_config
        self.app = BaseFlask(__name__)
        self.ordbok = self.app.config
        self.ordbok.root_path = os.getcwd()  # the fudged files are here

    def test_flask_helper(self):
        self.assertIsInstance(self.app.config, OrdbokFlaskConfig)
