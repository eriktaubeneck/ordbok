### YAML Config Files
As your Flask application grows, you may find that your configuration is coming from all over the place, and it may be difficult to understand what is overriding what. Ordbok adds a strict order of operations as to how the config should be loaded, and tools to specify that a certain variable should be specified later in the chain.

The default configurations has three configuration steps:

1. `config.yml`
2. `local_config.yml`
3. Environmental Variables

YAML already has some structure like this, but the idea behind the `local_config.yml` is for settings that may be dependent of a developers own configuration.

Variables that show up in multiple files will assume the value in the later declaration. Moreover, variables can be declared in earlier files such that they must be found in later file or the environment. This works with the `<near_miss_key>`, which defaults to `ordbok` but can be specified. For example setting `KEY: 'ordbok_local_config'` in `config.yml` will raise an exception if `KEY` isn't specified in `local_config.yml`.

###OS Environmental Config
Config variables can be loaded from the OS environment just like the YAML config files, and is the last in the hierarchy of config variables sources. Config variables are loaded from the OS environment in two ways:

1. Every environmental variable of the form `ORDBOK_<KEY>` will be loaded into the Ordbok config dict as `'<KEY>':value` (where `value` is the value of the environmental variable.)

2. In any YAML config file, setting `KEY: ordbok_env_conifg_<env_var>` will look for `<ENV_VAR>` in the OS Environment and load the value into the Ordbok config dict as `'KEY': value`.

Specifying `KEY: 'ordbok_env_config'` or `KEY: 'ordbok_env_config_<env_var>'` in any of the YAML config files will raise an exception if `ORDBOK_KEY` isn't specified in the environment.

NOTE: OS Environment variables and Ordbok config dict keys are assumed to be uppercase (`ENV_VAR` and `'KEY'` respectively), even if the value is specified in lowercase (`env_var`.)
