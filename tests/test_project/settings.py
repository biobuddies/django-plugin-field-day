"""Test project Django settings."""

import djp

SECRET_KEY = 'django-insecure-test-key'  # noqa: S105
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes']

MIDDLEWARE = []

ROOT_URLCONF = 'tests.test_project.urls'

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'APP_DIRS': True}]

USE_TZ = True

djp.settings(globals())
