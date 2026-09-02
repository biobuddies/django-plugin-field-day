"""Tests for the validated postal address fields."""

import pytest
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError

from django_plugin_field_day.forms import AddressForm
from django_plugin_field_day.models import Address


def valid(**overrides: object) -> dict:
    return {
        'recipient': 'Jane Roe',
        'country_id': 'US',
        'street1': '1600 Pennsylvania Ave NW',
        'city': 'Washington',
        'subdivision_id': 'US-DC',
        'postal_code': '20500',
        **overrides,
    }


def posted(**overrides: object) -> dict:
    return {
        'recipient': 'Jane Roe',
        'country': 'US',
        'street1': '1600 Pennsylvania Ave NW',
        'city': 'Washington',
        'subdivision': 'US-DC',
        'postal_code': '20500',
        **overrides,
    }


@pytest.mark.django_db
def test_valid_us_address_saves():
    Address.objects.create(**valid())
    assert Address.objects.count() == 1


@pytest.mark.django_db
def test_gb_needs_no_subdivision():
    Address.objects.create(
        recipient='John Doe',
        country_id='GB',
        street1='10 Downing Street',
        city='London',
        postal_code='SW1A 2AA',
    )
    assert Address.objects.get().subdivision_id is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    'overrides',
    (
        {'country_id': 'CN', 'subdivision_id': None, 'postal_code': '100000'},  # region required
        {'postal_code': '2050'},  # US ZIP too short
        {'subdivision_id': 'GB-ENG'},  # region not in US
        {'street1': 'Line one\nLine two'},  # embedded newline
        {'street2': '', 'street3': 'Floor 3'},  # gap in street lines
        {'street2': '   '},  # present but blank optional line
    ),
)
def test_database_rejects(overrides: dict):
    with pytest.raises(IntegrityError), transaction.atomic():
        Address.objects.create(**valid(**overrides))


@pytest.mark.django_db
def test_line_too_long_fails_validation():
    with pytest.raises(ValidationError):
        Address(**valid(street1='x' * 36)).full_clean()


@pytest.mark.django_db
def test_form_collapses_whitespace_and_keeps_empty_line_empty():
    form = AddressForm(posted(street1='1600   Pennsylvania   Ave', street2=''))
    assert form.is_valid(), form.errors
    address = form.save()
    assert address.street1 == '1600 Pennsylvania Ave'
    assert address.street2 == ''


@pytest.mark.django_db
def test_form_rejects_bad_postal_code():
    form = AddressForm(posted(postal_code='oops'))
    assert not form.is_valid()
    assert 'postal_code_matches_country' in repr(form.errors)
