import os
import unittest
import mock
import fudge
from copy import deepcopy
from yaml.scanner import ScannerError

from flask import Flask

from ordbok.flask_helper import FlaskOrdbok
from ordbok import Ordbok, ConfigFile, PrivateConfigFile
from ordbok.util import create_config_file
from ordbok.exceptions import (
    OrdbokLowercaseKeyException, OrdbokMissingConfigFileException,
    OrdbokAmbiguousConfigFileException, OrdbokSelfReferenceException,
    OrdbokPreviouslyLoadedException, OrdbokNestedRequiredKeyException,
    OrdbokMissingKeyException, OrdbokMissingPrivateKeyException,
    OrdbokTargetedEnvKeyException, OrdbokMissingPrivateConfigFile,
    OrdbokMissingEncryptedPrivateConfigFile)


from tests.files import (
    fudged_config_files, fudged_config_no_local_file,
    patched_environ, fake_file_factory, fake_path_exists_factory)


class OrdbokTestCase(unittest.TestCase):
    def setUp(self):
        self.ordbok = Ordbok()

    def test_ordbok_defaults(self):
        self.assertEqual(self.ordbok.config_files,
                         ['config.yml', 'local_config.yml'])
        self.assertEqual(self.ordbok.config_dir, 'config')
        self.assertTrue(self.ordbok.include_env)
        self.assertEqual(self.ordbok.namespace, 'ordbok')
        self.assertEqual(self.ordbok.default_environment, 'development')

    @fudge.patch('six.moves.builtins.open')
    def test_ordbok_load(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        self.ordbok.load()
        self.assertEquals(self.ordbok['ENVIRONMENT'], 'development')
        self.assertEquals(self.ordbok['SECRET_KEY'], 'keep out!')
        self.assertTrue(self.ordbok['DEBUG'])
        self.assertEquals(self.ordbok['SQLALCHEMY_DATABASE_URL'],
                          'sqlite:///tmp/database.db')
        self.assertTrue(self.ordbok['SQLALCHEMY_ECHO'])

    @fudge.patch('six.moves.builtins.open')
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

    @fudge.patch('six.moves.builtins.open')
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

    @fudge.patch('six.moves.builtins.open')
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

    @fudge.patch('six.moves.builtins.open')
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

    @fudge.patch('six.moves.builtins.open')
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

    @fudge.patch('six.moves.builtins.open')
    def test_missing_config_file_ordbok_load(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'config.yml': u"""
            FOO: 'ordbok_foo_config'
            """})
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_copy))
        with self.assertRaises(OrdbokMissingConfigFileException):
            self.ordbok.load()

    @fudge.patch('six.moves.builtins.open')
    def test_ambiguous_config_file_ordbok_load(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'local_con.yml': u"""
            FOO: 'bar'
            """})
        self.ordbok.config_files.append('local_con.yml')
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_copy))
        with self.assertRaises(OrdbokAmbiguousConfigFileException):
            self.ordbok.load()

    @fudge.patch('six.moves.builtins.open')
    def test_self_reference_ordbok_load(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'local_config.yml': u"""
            FOO: 'ordbok_local_config'
            """})
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_copy))
        with self.assertRaises(OrdbokSelfReferenceException):
            self.ordbok.load()

    @fudge.patch('six.moves.builtins.open')
    def test_previously_loaded_ordbok_load(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'local_config.yml': u"""
            FOO: 'ordbok_config'
            """})
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_copy))
        with self.assertRaises(OrdbokPreviouslyLoadedException):
            self.ordbok.load()

    @fudge.patch('six.moves.builtins.open')
    def test_nested_keys_ordbok_load(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'config.yml': u"""
            FOO:
                BAZ:
                    BAR:
                        BAZZZZ: 'ordbok_local_config'
            """})
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_copy))
        with self.assertRaises(OrdbokNestedRequiredKeyException):
            self.ordbok.load()

    @fudge.patch('six.moves.builtins.open')
    def test_missing_key_ordbok_load(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'config.yml': u"""
            FOO: 'ordbok_local_config'
            """})
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_copy))
        with self.assertRaises(OrdbokMissingKeyException):
            self.ordbok.load()

    @fudge.patch('six.moves.builtins.open')
    @mock.patch.dict('os.environ', patched_environ)
    def test_missing_targeted_env_key_ordbok_load(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        fudged_config_files_copy = deepcopy(fudged_config_files)
        fudged_config_files_copy.update({
            u'config.yml': u"""
            FOO: 'ordbok_env_config_not_there'
            """})
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_copy))
        with self.assertRaises(OrdbokTargetedEnvKeyException):
            self.ordbok.load()


class OrdbokConfigFileTestCase(unittest.TestCase):
    def setUp(self):
        self.ordbok = Ordbok()
        self.config_file = ConfigFile('config.yml')
        self.config_file.init_config(self.ordbok)

    def test_file_add_required_keys(self):
        self.config_file.add_required_key('foo')
        self.config_file.add_required_key('bar', 'baz')
        self.assertIn('foo', self.config_file.required_keys)
        self.assertIn('bar', self.config_file.required_keys)
        self.assertNotIn('baz', self.config_file.required_keys)

    def test_file_validate_yaml_content(self):
        with self.assertRaises(TypeError):
            self.config_file._validate_yaml_content(['foo', 'bar', 'baz'])
        self.config_file._validate_yaml_content({'foos': ['foo', 'bar', 'baz']})

    def test_file_validate_key(self):
        with self.assertRaises(OrdbokLowercaseKeyException):
            self.config_file._validate_key('foo')
        self.config_file._validate_key('FOO')

    def test_create_config_file(self):
        with self.assertRaises(TypeError):
            create_config_file(1)
        with self.assertRaises(TypeError):
            create_config_file({'foo': 'bar'})
        with self.assertRaises(TypeError):
            create_config_file(['foo', 'bar'])


class OrdbokPrivateConfigFileTestCase(unittest.TestCase):
    def setUp(self):
        self.private_config_file = PrivateConfigFile(
            'private_config.yml', envs=['production'])
        self.ordbok = Ordbok(
            config_files=['config.yml', 'local_config.yml',
                          self.private_config_file]
        )

    @unittest.skipIf(os.environ.get('SKIP_ENCRYPT_TEST'),
                     'as env var to skip lengthy test')
    @fudge.patch('ordbok.config_private.open_wrapper')
    def test_ordbok_private_config(self, fudged_open):
        fudged_config_files_with_private = deepcopy(fudged_config_files)
        fudged_config_files_with_private.update({
            u'private_config.yml': u"""
            OAUTH_KEY: 'super_secret_key'
            OAUTH_SECRET: 'even_secreter_secret'
            """,
        })

        # set directly instead of completely rewriting 'config.yml'
        self.ordbok['PRIVATE_KEY_ORDBOK'] = 'foobarbaz'
        self.private_config_file.init_config(self.ordbok)

        encrypted_content = self.private_config_file._encrypt_content(
            fudged_config_files_with_private[u'private_config.yml'])
        fudged_config_files_with_private.update({
            u'private_config.yml.private': encrypted_content,
        })
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_with_private))

        self.ordbok['ENVIRONMENT'] = 'production'
        self.ordbok.load()

        self.assertEquals(self.ordbok['OAUTH_KEY'], 'super_secret_key')
        self.assertEquals(self.ordbok['OAUTH_SECRET'], 'even_secreter_secret')

    @fudge.patch('ordbok.config_private.open_wrapper')
    @fudge.patch('os.path.exists')
    def test_ordbok_private_config_no_encrypted_file(
            self, fudged_open, fudged_path_exists):
        fudged_config_files_with_private = deepcopy(fudged_config_files)
        fudged_config_files_with_private.update({
            u'private_config.yml': u"""
            OAUTH_KEY: 'super_secret_key'
            OAUTH_SECRET: 'even_secreter_secret'
            """,
        })

        # set directly instead of completely rewriting 'config.yml'
        self.ordbok['PRIVATE_KEY_ORDBOK'] = 'foobarbaz'
        self.private_config_file.init_config(self.ordbok)

        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_with_private))
        fudged_path_exists.is_callable().calls(
            fake_path_exists_factory(fudged_config_files_with_private))

        self.ordbok['ENVIRONMENT'] = 'production'

        with self.assertRaises(OrdbokMissingEncryptedPrivateConfigFile):
            self.ordbok.load()

    @fudge.patch('ordbok.config_private.open_wrapper')
    @fudge.patch('os.path.exists')
    def test_ordbok_private_config_no_file(
            self, fudged_open, fudged_path_exists):
        # set directly instead of completely rewriting 'config.yml'
        self.ordbok['PRIVATE_KEY_ORDBOK'] = 'foobarbaz'
        self.private_config_file.init_config(self.ordbok)

        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files))
        fudged_path_exists.is_callable().calls(
            fake_path_exists_factory(fudged_config_files))

        self.ordbok['ENVIRONMENT'] = 'production'

        with self.assertRaises(OrdbokMissingPrivateConfigFile):
            self.ordbok.load()

    @fudge.patch('ordbok.config_private.open_wrapper')
    @fudge.patch('os.path.exists')
    def test_ordbok_private_config_load_decrypted(
            self, fudged_open, fudged_path_exists):
        fudged_config_files_with_private = deepcopy(fudged_config_files)
        file_content = u"""
            OAUTH_KEY: 'super_secret_key'
            OAUTH_SECRET: 'even_secreter_secret'
            """
        fudged_config_files_with_private.update({
            u'private_config.yml': file_content
        })

        # set directly instead of completely rewriting 'config.yml'
        self.ordbok['PRIVATE_KEY_ORDBOK'] = 'foobarbaz'
        self.private_config_file.init_config(self.ordbok)

        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files_with_private))
        fudged_path_exists.is_callable().calls(
            fake_path_exists_factory(fudged_config_files_with_private))

        self.ordbok['ENVIRONMENT'] = 'production'

        decrypted_file = self.private_config_file._load_decrypted_file()
        self.assertEqual(file_content, decrypted_file)

    @fudge.patch('ordbok.config_private.open_wrapper')
    @fudge.patch('os.path.exists')
    def test_ordbok_private_config_load_decrypted_no_file(
            self, fudged_open, fudged_path_exists):
        # set directly instead of completely rewriting 'config.yml'
        self.ordbok['PRIVATE_KEY_ORDBOK'] = 'foobarbaz'
        self.private_config_file.init_config(self.ordbok)

        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files))
        fudged_path_exists.is_callable().calls(
            fake_path_exists_factory(fudged_config_files))

        self.ordbok['ENVIRONMENT'] = 'production'

        with self.assertRaises(OrdbokMissingPrivateConfigFile):
            self.private_config_file._load_decrypted_file()

    @fudge.patch('ordbok.config_private.open_wrapper')
    @mock.patch.object(PrivateConfigFile, '_load_yaml')
    def test_ordbok_private_config_envs(
            self, fudged_open, mock_load_yaml):
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files))
        mock_load_yaml.return_value = ''
        self.ordbok.load()
        self.assertFalse(mock_load_yaml.called)

    @fudge.patch('ordbok.config_private.open_wrapper')
    def test_ordbok_private_config_no_private_key(self, fudged_open):
        self.ordbok['ENVIRONMENT'] = 'production'
        fudged_config_files.update({
            u'private_config.yml.private': 'foobarbaz',
        })
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        with self.assertRaises(OrdbokMissingPrivateKeyException):
            self.ordbok.load()

    @fudge.patch('ordbok.config_private.open_wrapper')
    @mock.patch.object(PrivateConfigFile, '_load_yaml')
    def test_ordbok_private_config_no_envs(
            self, fudged_open, mock_load_yaml):
        fudged_open.is_callable().calls(
            fake_file_factory(fudged_config_files))
        mock_load_yaml.return_value = ''
        self.ordbok['ENVIRONMENT'] = 'production'
        self.ordbok.load()
        self.assertTrue(mock_load_yaml.called)

    def test_ordbok_private_key(self):
        self.ordbok['PRIVATE_KEY_ORDBOK'] = 'foobarbaz'
        self.assertEqual(self.ordbok.private_file_key, 'foobarbaz')


class OrdbokDefaultsTestCase(unittest.TestCase):
    def test_update_all_defaults(self):
        Ordbok(config_dir='ordbok_config',
               config_files=['config.yml'],
               include_env=False,
               namespace='ordbok_foo',
               default_environment='testing',)

    def test_update_config_dir(self):
        Ordbok(config_dir='ordbok_config',)

    def test_update_config_files(self):
        Ordbok(config_files=['config.yml'],)

    def test_update_include_env(self):
        Ordbok(include_env=False,)

    def test_update_namespace(self):
        Ordbok(namespace='ordbok_foo',)

    def test_update_default_environment(self):
        Ordbok(default_environment='testing',)


class FlaskOrdbokTestCase(OrdbokTestCase):
    def setUp(self):
        self.app = Flask(os.getcwd())  # fudged files think they are in cwd
        self.ordbok = FlaskOrdbok(app=self.app)

    @fudge.patch('six.moves.builtins.open')
    def test_flask_config_update(self, fudged_open):
        fudged_open.is_callable().calls(fake_file_factory(fudged_config_files))
        self.ordbok.load()
        self.app.config.update(self.ordbok)
        self.assertEquals(self.app.config['ENVIRONMENT'], 'development')
        self.assertEquals(self.app.config['SECRET_KEY'], 'keep out!')
        self.assertTrue(self.app.config['DEBUG'])
        self.assertEquals(self.app.config['SQLALCHEMY_DATABASE_URL'],
                          'sqlite:///tmp/database.db')
        self.assertTrue(self.app.config['SQLALCHEMY_ECHO'])

    @mock.patch.object(Flask, 'run')
    def test_flask_reloader(self, fudged_flask_run):
        self.ordbok.load()
        self.app.debug = True
        self.ordbok.app_run(self.app)
        fudged_flask_run.assert_called()
        fudged_flask_run.assert_called_with(
            extra_files=self.ordbok.config_file_names)

    @mock.patch.object(Flask, 'run')
    def test_flask_reloader_debug_off(self, fudged_flask_run):
        self.ordbok.load()
        self.ordbok.app_run(self.app)
        fudged_flask_run.assert_called()
        fudged_flask_run.assert_called_with()  # no extra files

    @mock.patch.object(Flask, 'run')
    def test_flask_reloader_use_reloader_false(self, fudged_flask_run):
        self.ordbok.load()
        self.ordbok.app_run(self.app, use_reloader=False)
        fudged_flask_run.assert_called()
        fudged_flask_run.assert_called_with(use_reloader=False)  # no extra files


class SpecialFlaskOrdbokTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.ordbok = FlaskOrdbok(app=self.app)

    def test_root_path(self):
        """
        Generally this should be True, however in the above tests
        the way open() was monkey patched required us to override
        this for the the tests.
        """
        self.assertEquals(self.app.root_path, self.ordbok.config_cwd)
