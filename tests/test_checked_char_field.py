"""Tests for CheckedCharField checked at the Python, HTML, and database levels."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import modelform_factory
from pytest import mark, raises

from tests.models import CheckedCharExample


@mark.django_db
def test_blank_is_allowed_when_min_length_is_zero():
    CheckedCharExample(pair='ab').full_clean()


@mark.django_db
@mark.parametrize(('field', 'value'), (('letters', 'ABCDE'), ('pair', 'a'), ('pair', 'abc')))
def test_validators_reject_wrong_lengths(field: str, value: str):
    with raises(ValidationError, match=field):
        CheckedCharExample(**{'pair': 'ab', field: value}).full_clean()


def test_form_carries_html_constraints():
    fields = modelform_factory(CheckedCharExample, fields=['letters', 'pair'])().fields
    assert [
        (fields[name].widget.attrs['minlength'], fields[name].widget.attrs['maxlength'])
        for name in ('letters', 'pair')
    ] == [(0, 4), (2, 2)]


@mark.django_db
@mark.parametrize(('field', 'value'), (('letters', 'ABCDE'), ('pair', 'a'), ('pair', 'abc')))
def test_database_rejects_wrong_lengths(field: str, value: str):
    with raises(IntegrityError):
        CheckedCharExample.objects.create(**{'pair': 'ab', field: value})
