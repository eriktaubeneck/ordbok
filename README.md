# Ordbok

[![Build Status](https://travis-ci.org/eriktaubeneck/ordbok.svg?branch=master)](https://travis-ci.org/eriktaubeneck/ordbok)
[![Coverage Status](https://img.shields.io/coveralls/eriktaubeneck/ordbok.svg)](https://coveralls.io/r/eriktaubeneck/ordbok)
[![Code Climate](https://codeclimate.com/github/eriktaubeneck/ordbok/badges/gpa.svg)](https://codeclimate.com/github/eriktaubeneck/ordbok)
[![Documentation Status](https://readthedocs.org/projects/ordbok/badge/?version=latest)](https://readthedocs.org/projects/ordbok/?badge=latest)
[![Latest Version](https://pypip.in/version/ordbok/badge.png)](https://pypi.python.org/pypi/ordbok/)
[![Downloads](https://pypip.in/download/ordbok/badge.png)](https://pypi.python.org/pypi/ordbok/)
[![License](https://pypip.in/license/ordbok/badge.png)](https://pypi.python.org/pypi/ordbok/)

As your application grows, configuration can get a bit chaotic, especially if you have multiple versions (local, deployed, staging, etc.) Ordbok brings order to that chaos.

Ordbok abstracts the loading of a configuration from YAML files into a Python dictionary, and also has a specific setup for use with Flask. See [TODO](#todo) for plans to expand this.

![Svenska Akademiens ordbok](http://fc01.deviantart.net/fs70/i/2011/048/b/1/svenska_akademiens_ordbok_by_droemmaskin-d39rta7.jpg)
_<a href="http://droemmaskin.deviantart.com/art/Svenska-Akademiens-ordbok-197812735">Svenska Akademiens ordbok</a> by <span class="username-with-symbol u"><a class="u regular username" href="http://droemmaskin.deviantart.com/">droemmaskin</a><span class="user-symbol regular" data-quicktip-text="" data-show-tooltip="" data-gruser-type="regular"></span></span> on <a href="http://www.deviantart.com">deviantART</a>. Provided under [Attribution-NonCommercial-ShareAlike 3.0 Unported](http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode)_


## Docs

[Full Docs](http://ordbok.readthedocs.org/en/latest) hosted by Read the Docs.

## Basic Usage

Ordbok is designed to allow users to define a hierarchy of YAML configuration files and specify environments. The default configuration has three tiers: `config.yml`, `local_config.yml`, and Environmental Variables. The later tiers override the earlier ones, and earlier configurations can explicitly require certain variables to be defined in a later one. This can be particularly useful when you expect, say, certain variables to be specified in the environment on a production server and want to fail hard and explicitly when that variable isn't present.

## Installation

Inside a [virtualenv](http://virtualenv.readthedocs.org/en/latest/) run

```
pip install ordbok
```

## Quickstart

```
from ordbok import Ordbok
config = Ordbok()
config.load()
```

Then, in your app root path, create a directory `config` and add two files `config.yml` and `local_config.yml`. See the [examples](http://ordbok.readthedocs.org/en/latest/usage/examples/) for an example YAML configuration.
