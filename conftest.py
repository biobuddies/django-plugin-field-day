"""Django plugin field day test configuration."""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_project.settings')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')


def pytest_configure() -> None:
    django.setup()
