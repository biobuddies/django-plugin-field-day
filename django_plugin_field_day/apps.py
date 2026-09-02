"""Django application configuration."""

from django.apps import AppConfig


class DjangoPluginFieldDayConfig(AppConfig):
    """Register the field-day models and migrations."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_plugin_field_day'
