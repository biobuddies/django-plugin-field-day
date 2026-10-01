"""Tests for CheckedColorField: 24-bit integers that print as #rrggbb."""

from django.contrib.admin import ModelAdmin, site
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Value
from django.forms import modelform_factory
from django.test import RequestFactory
from pytest import mark, raises

from django_plugin_field_day import format_color
from django_plugin_field_day.fields import Color, ColorInput
from tests.models import CheckedColorExample


@mark.parametrize(
    ('given', 'number'),
    (
        ('#000000', 0),
        ('#FFFFFF', 0xFFFFFF),
        ('#aBcDeF', 0xABCDEF),
        ('#0a0b0c', 0x0A0B0C),
        (0x00000A, 10),
        (Color('#123456'), 0x123456),
    ),
)
def test_color_accepts_any_case(given: int | str, number: int):
    assert Color(given) == number


@mark.parametrize(
    ('given', 'printed'),
    (('#AbCdEf', '#abcdef'), (10, '#00000a'), (0, '#000000'), (0xFFFFFF, '#ffffff')),
)
def test_color_prints_lowercase_pound_six_hex(given: int | str, printed: str):
    assert str(Color(given)) == printed


@mark.parametrize(
    'given',
    (
        '#fffffg',
        'ffffff',
        '#fff',
        '#fffffff',
        '#ffffff ',
        ' #ffffff',
        '#ffffff\n',
        '#ff_fff',
        '#-fffff',
        '#' + '\u0660' * 6,
        'red',
        '',
        '#',
        -1,
        0x1000000,
        1.5,
        True,
        None,
    ),
)
def test_color_rejects_malformed(given: object):
    with raises(ValidationError) as caught:
        Color(given)  # pyrefly: ignore[bad-argument-type]
    assert caught.value.code == 'invalid'


@mark.django_db
def test_model_validation_normalizes():
    icon = CheckedColorExample(foreground='#ABCDef', background=0)
    icon.full_clean()
    assert (icon.foreground, icon.background) == (0xABCDEF, 0)
    assert str(icon.foreground) == '#abcdef'


@mark.django_db
def test_model_validation_rejects_malformed():
    with raises(ValidationError) as caught:
        CheckedColorExample(foreground='#fffffg').full_clean()
    assert caught.value.error_dict['foreground'][0].code == 'invalid'


def test_defaults_are_colors():
    icon = CheckedColorExample()
    assert (str(icon.foreground), str(icon.background)) == ('#000000', '#ffffff')


@mark.django_db
def test_round_trip_returns_colors():
    icon = CheckedColorExample.objects.create(foreground='#FF8000')
    icon.refresh_from_db()
    assert isinstance(icon.foreground, Color)
    assert str(icon.foreground) == '#ff8000'
    assert CheckedColorExample.objects.filter(foreground='#FF8000').count() == 1
    assert (
        CheckedColorExample.objects.filter(foreground__gt=0xFF7FFF, foreground__lt=0xFF8001).count()
        == 1
    )


@mark.django_db
@mark.parametrize('number', (0, 1, 10, 15, 16, 255, 0x0F0F0F, 0x123456, 0xABCDEF, 0xFFFFFF))
def test_format_color_matches_python(number: int):
    CheckedColorExample.objects.create(foreground=number)
    css = CheckedColorExample.objects.annotate(css=format_color('foreground')).values_list(
        'css', flat=True
    )
    assert css.get() == str(Color(number))


@mark.django_db
@mark.parametrize('number', (-1, 0x1000000))
def test_database_rejects_out_of_range(number: int):
    icon = CheckedColorExample.objects.create()
    with raises(IntegrityError):
        CheckedColorExample.objects.filter(pk=icon.pk).update(foreground=Value(number))


def test_form_uses_native_color_input():
    form = modelform_factory(CheckedColorExample, fields=['foreground'])()
    assert isinstance(form.fields['foreground'].widget, ColorInput)
    assert form.fields['foreground'].widget.input_type == 'color'


def test_admin_keeps_native_color_input(rf: RequestFactory):
    form = ModelAdmin(CheckedColorExample, site).get_form(rf.get('/'))()
    assert form.fields['foreground'].widget.input_type == 'color'


@mark.django_db
def test_form_cleans_to_color():
    form = modelform_factory(CheckedColorExample, fields=['foreground', 'background'])({
        'foreground': '#FFAA00',
        'background': '#fffffg',
    })
    assert not form.is_valid()
    assert list(form.errors) == ['background']
    assert form.cleaned_data['foreground'] == 0xFFAA00


def test_form_unchanged_initial_is_unchanged():
    form_class = modelform_factory(CheckedColorExample, fields=['foreground'])
    assert not form_class({'foreground': '#000000'}).has_changed()
    assert form_class({'foreground': '#000001'}).has_changed()
