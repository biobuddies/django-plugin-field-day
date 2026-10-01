"""Tests for StringField checked at the Python, HTML, and database levels."""

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection
from django.forms import modelform_factory
from pytest import mark, raises

from django_plugin_field_day.fields import StringField
from tests.models import StringExample

VALID = {'code': 'AB', 'letters': '', 'slug': 'a'}


@mark.parametrize(
    ('regex', 'internal_type', 'min_length', 'max_length', 'blank'),
    (
        ('[A-Z]{2}', 'CharField', 2, 2, False),
        ('.{0,4}', 'CharField', 0, 4, True),
        ('(ab|cde)?', 'CharField', 0, 3, True),
        ('[a-z]+', 'TextField', 1, None, False),
        ('.*', 'TextField', 0, None, True),
        ('.{0,10485760}', 'CharField', 0, 10485760, True),
        ('.{0,10485761}', 'TextField', 0, None, True),
    ),
)
def test_width_and_blank_come_from_regex(
    regex: str, internal_type: str, min_length: int, max_length: int | None, blank: bool
):
    field = StringField(regex=regex)
    assert (field.get_internal_type(), field.min_length, field.max_length, field.blank) == (
        internal_type,
        min_length,
        max_length,
        blank,
    )


def test_blank_cannot_contradict_regex():
    with raises(ValueError, match='contradicts'):
        StringField(regex='[A-Z]', blank=True)


def test_deconstruct_keeps_only_regex():
    assert StringField(regex='.{0,4}').deconstruct()[3] == {'regex': '.{0,4}'}


def test_database_types():
    assert [
        StringExample._meta.get_field(name).db_type(connection)
        for name in ('code', 'letters', 'slug')
    ] == ['varchar(2)', 'varchar(4)', 'text']


@mark.django_db
@mark.parametrize(
    ('field', 'value'), (('code', 'AB'), ('letters', ''), ('letters', 'abcd'), ('slug', 'a-b'))
)
def test_matching_values_are_valid(field: str, value: str):
    StringExample(**{**VALID, field: value}).full_clean()


@mark.django_db
@mark.parametrize(
    ('field', 'value'),
    (
        ('code', 'A'),
        ('code', 'ABC'),
        ('code', 'ab'),
        ('code', 'xABx'),
        ('code', 'AB\n'),
        ('code', ''),
        ('letters', 'abcde'),
        ('slug', 'a_b'),
        ('slug', '-a'),
        ('slug', ''),
    ),
)
def test_validators_require_a_full_match(field: str, value: str):
    with raises(ValidationError, match=field):
        StringExample(**{**VALID, field: value}).full_clean()


@mark.django_db
@mark.parametrize(
    ('field', 'value'),
    (('code', 'A'), ('code', 'xABx'), ('code', 'ab'), ('letters', 'abcde'), ('slug', 'a_b')),
)
def test_database_rejects_mismatches(field: str, value: str):
    with raises(IntegrityError):
        StringExample.objects.create(**{**VALID, field: value})


def test_form_carries_html_constraints():
    fields = modelform_factory(StringExample, fields=['code', 'letters', 'slug'])().fields
    assert [
        (
            fields[name].widget.attrs['pattern'],
            fields[name].widget.attrs['minlength'],
            fields[name].widget.attrs.get('maxlength'),
            fields[name].required,
        )
        for name in ('code', 'letters', 'slug')
    ] == [
        ('[A-Z]{2}', '2', '2', True),
        ('.{0,4}', '0', '4', False),
        ('[a-z]+(-[a-z]+)*', '1', None, True),
    ]
