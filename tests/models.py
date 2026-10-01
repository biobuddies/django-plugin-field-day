"""Models that exercise fields in isolation; the test database creates their tables."""

from django.db.models import Model

from django_plugin_field_day.colors import ColorField
from django_plugin_field_day.fields import NumberField, StringField


class NumberExample(Model):  # noqa: DJ008
    percent = NumberField(minimum=0, maximum=100)
    floor = NumberField(minimum=-5)
    wide = NumberField(minimum=0, maximum=2**40)


class StringExample(Model):  # noqa: DJ008
    code = StringField(regex='[A-Z]{2}')
    letters = StringField(regex='.{0,4}')
    slug = StringField(regex='[a-z]+(-[a-z]+)*')


class ColorExample(Model):  # noqa: DJ008
    foreground = ColorField(default='#000000')
    background = ColorField(default='#ffffff')
