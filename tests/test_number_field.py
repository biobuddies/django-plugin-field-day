"""Tests for NumberField checked at the Python, HTML, and database levels."""

from django.contrib.admin import ModelAdmin, site
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Value
from django.forms import modelform_factory
from django.test import RequestFactory
from pytest import mark, raises

from django_plugin_field_day.fields import NumberField
from tests.models import NumberExample

VALID = {'percent': 50, 'floor': 0, 'wide': 1}


@mark.django_db
@mark.parametrize(
    ('field', 'value'), (('percent', 0), ('percent', 100), ('floor', -5), ('wide', 2**40))
)
def test_bounds_are_inclusive(field: str, value: int):
    NumberExample(**{**VALID, field: value}).full_clean()


@mark.django_db
@mark.parametrize(
    ('field', 'value'), (('percent', -1), ('percent', 101), ('floor', -6), ('wide', 2**40 + 1))
)
def test_validators_reject_out_of_bounds(field: str, value: int):
    with raises(ValidationError, match=field):
        NumberExample(**{**VALID, field: value}).full_clean()


@mark.django_db
@mark.parametrize(('field', 'value'), (('percent', -1), ('percent', 101), ('floor', -6)))
def test_database_rejects_out_of_bounds(field: str, value: int):
    example = NumberExample.objects.create(**VALID)
    with raises(IntegrityError):
        NumberExample.objects.filter(pk=example.pk).update(**{field: Value(value)})


@mark.parametrize(
    ('minimum', 'maximum', 'internal_type'),
    (
        (0, 100, 'SmallIntegerField'),
        (-(2**15), 2**15 - 1, 'SmallIntegerField'),
        (0, 2**15, 'IntegerField'),
        (None, None, 'IntegerField'),
        (0, None, 'IntegerField'),
        (-(2**31), 2**31 - 1, 'IntegerField'),
        (-(2**31) - 1, 0, 'BigIntegerField'),
        (0, 2**40, 'BigIntegerField'),
    ),
)
def test_smallest_database_type_that_fits(
    minimum: int | None, maximum: int | None, internal_type: str
):
    assert NumberField(minimum=minimum, maximum=maximum).get_internal_type() == internal_type


def test_minimum_above_maximum_is_rejected():
    with raises(ValueError, match='exceeds'):
        NumberField(minimum=2, maximum=1)


def test_deconstruct_omits_open_bounds():
    assert NumberField(minimum=0).deconstruct()[3] == {'minimum': 0}


def test_form_carries_html_constraints():
    fields = modelform_factory(NumberExample, fields=['percent', 'floor'])().fields
    assert fields['percent'].widget.attrs['min'] == 0
    assert fields['percent'].widget.attrs['max'] == 100
    assert fields['floor'].widget.attrs['min'] == -5
    assert 'max' not in fields['floor'].widget.attrs


def test_admin_keeps_html_constraints(rf: RequestFactory):
    fields = ModelAdmin(NumberExample, site).get_form(rf.get('/'))().fields
    assert (fields['percent'].widget.attrs['min'], fields['percent'].widget.attrs['max']) == (
        0,
        100,
    )
