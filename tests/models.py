"""Models that exercise fields in isolation; the test database creates their tables."""

from django.db.models import Model

from django_plugin_field_day.fields import CheckedCharField


class CheckedCharExample(Model):  # noqa: DJ008
    letters = CheckedCharField(blank=True, max_length=4, min_length=0)
    pair = CheckedCharField(max_length=2, min_length=2)
