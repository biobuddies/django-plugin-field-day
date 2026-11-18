"""Models that exercise fields in isolation; the test database creates their tables."""

from django.db.models import Model

from django_plugin_field_day.fields import NumberField


class NumberExample(Model):  # noqa: DJ008
    percent = NumberField(minimum=0, maximum=100)
    floor = NumberField(minimum=-5)
    wide = NumberField(minimum=0, maximum=2**40)
