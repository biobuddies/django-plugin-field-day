"""Tests for the Icon model: its fields are covered in detail by their own tests."""

from django.contrib.admin import site
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from pytest import mark, raises

from django_plugin_field_day.admin import IconAdmin
from django_plugin_field_day.models import Icon


@mark.django_db
def test_defaults_are_valid():
    icon = Icon()
    icon.full_clean()
    assert (str(icon), str(icon.foreground), str(icon.background)) == ('', '#000000', '#ffffff')


@mark.django_db
def test_letters_are_limited_to_four_characters():
    with raises(ValidationError, match='letters'):
        Icon(letters='ABCDE').full_clean()


def test_str_prefers_letters_to_svg():
    assert str(Icon(letters='K', svg='k.svg')) == 'K'
    assert str(Icon(svg='k.svg')) == 'k.svg'


def test_admin_form_carries_html_constraints(rf: RequestFactory):
    fields = IconAdmin(Icon, site).get_form(rf.get('/'))().fields
    assert fields['letters'].widget.attrs['maxlength'] == '4'
    assert [fields[name].widget.input_type for name in ('foreground', 'background')] == [
        'color',
        'color',
    ]
