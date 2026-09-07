"""Tests for the Region (ISO 3166-2 Subdivision) model."""

from django.db import IntegrityError
from pytest import mark, raises

from django_plugin_field_day.models import Region


@mark.django_db
def test_data_migration_loads_the_states_and_dc():
    assert Region.objects.count() == 51
    assert Region.objects.get(pk='US-CA').name == 'California'


@mark.django_db
def test_code_is_the_primary_key():
    with raises(IntegrityError):
        Region.objects.create(code='US-CA', name='Duplicate')
