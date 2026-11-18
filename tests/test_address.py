"""Tests for the validated Address model and its CHECK constraints."""

from django.db import IntegrityError
from pytest import mark, raises

from django_plugin_field_day.models import Address

VALID = {
    'recipient': 'Jane Roe',
    'country_id': 'US',
    'street1': '1600 Pennsylvania Ave NW',
    'city': 'Washington',
    'region_id': 'US-DC',
    'postal_code': '20500',
}


@mark.django_db
def test_valid_address_saves():
    Address.objects.create(**VALID)
    assert Address.objects.count() == 1


@mark.django_db
def test_region_must_belong_to_country():
    with raises(IntegrityError):
        Address.objects.create(**(VALID | {'country_id': 'CA'}))


@mark.django_db
def test_rejects_control_characters():
    with raises(IntegrityError):
        Address.objects.create(**(VALID | {'street1': 'Line one\nLine two'}))


@mark.django_db
def test_rejects_street_line_gap():
    with raises(IntegrityError):
        Address.objects.create(**(VALID | {'street2': '', 'street3': 'Floor 3'}))


@mark.django_db
def test_rejects_blank_required_line():
    with raises(IntegrityError):
        Address.objects.create(**(VALID | {'city': '   '}))
