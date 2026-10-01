"""Tests for the Icon model checked at the Python, HTML, and database levels."""

from django.contrib.admin import site
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import RequestFactory
from pytest import mark, raises

from django_plugin_field_day.admin import IconAdmin
from django_plugin_field_day.models import Icon


@mark.django_db
def test_letters_and_svg_may_be_blank():
    Icon().full_clean()


@mark.django_db
def test_letters_are_limited_to_four_characters():
    with raises(ValidationError, match='letters'):
        Icon(letters='ABCDE').full_clean()


def test_admin_form_carries_html_constraints(rf: RequestFactory):
    widget = IconAdmin(Icon, site).get_form(rf.get('/'))().fields['letters'].widget
    assert (widget.attrs['minlength'], widget.attrs['maxlength']) == (0, 4)


@mark.django_db
def test_database_rejects_long_letters():
    with raises(IntegrityError):
        Icon.objects.create(letters='ABCDE')
