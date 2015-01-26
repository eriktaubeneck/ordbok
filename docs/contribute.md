## TODO

 - Add advanced Example to documentation
 - Add support for more file types (JSON, maybe XML?)
 - Add integrated support for other frameworks (Pyramid, Django, etc.)
 - Add a private config file type, where an encrypted version of the file could exist in the repo, and a password could be set in the environment where the private keys are used. Will require integration with Flask-Script to provide methods to decrypt locally with the password, edit keys, and re-encrypt. (In progress on branch `encrypted-config`.)


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

There is also a script, `run_tests.sh` which will run the tests in all three supported environments, assuming your Python 2.7 virtualenv is named `venv`, your PyPy virutalenv is named `venvpypy`, and your Python 3 virtualenv is named `venv3`.
