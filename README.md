# django-plugin-field-day

[![PyPI](https://img.shields.io/pypi/v/django-plugin-field-day.svg)](https://pypi.org/project/django-plugin-field-day/)
[![Changelog](https://img.shields.io/github/v/release/covingtron/django-plugin-field-day?include_prereleases&label=changelog)](https://github.com/covingtron/django-plugin-field-day/releases)
[![Tests](https://github.com/covingtron/django-plugin-field-day/workflows/Test/badge.svg)](https://github.com/covingtron/django-plugin-field-day/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-blue.svg)](https://github.com/covingtron/django-plugin-field-day/blob/main/LICENSE)

Additional and improved fields for Django

## Installation

First configure your Django project [to use DJP](https://djp.readthedocs.io/en/latest/installing_plugins.html).

Then install this plugin in the same environment as your Django application.
```bash
pip install django-plugin-field-day
```
## Usage

Usage instructions go here.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd django-plugin-field-day
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
