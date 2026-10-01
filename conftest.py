"""Django plugin field day test configuration."""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')


def pytest_configure() -> None:
    from django.conf import settings  # noqa: PLC0415

    # tests/models.py exercises fields without a model in the shipped app
    settings.INSTALLED_APPS = [*settings.INSTALLED_APPS, 'tests']
    django.setup()
