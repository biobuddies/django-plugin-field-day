"""Tests for the ISO 3166-1 Country reference table loaded by data migration."""

from django.db import IntegrityError
from pytest import mark, raises

from django_plugin_field_day.models import Country


@mark.django_db
def test_data_migration_loads_countries():
    assert Country.objects.count() == 252
    assert Country.objects.get(code='US').name == 'UNITED STATES'


@mark.django_db
def test_us_territories_are_part_of_us():
    assert sorted(Country.objects.filter(part_of='US').values_list('code', flat=True)) == [
        'AS',
        'GU',
        'MP',
        'PR',
        'UM',
        'VI',
    ]
    assert Country.objects.get(code='VI').part_of == Country.objects.get(code='US')


@mark.django_db
def test_code_is_the_primary_key():
    with raises(IntegrityError):
        Country.objects.create(code='US', name='DUPLICATE')
