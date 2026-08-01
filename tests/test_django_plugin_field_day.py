"""Tests for django-plugin-field-day."""

from datetime import datetime
from types import SimpleNamespace

from django.contrib.auth.models import User
from django.db.models import Value
from pytest import MonkeyPatch, mark
from pytest_django.fixtures import SettingsWrapper

from django_plugin_field_day import Left, Right, StrFTime


@mark.django_db
def test_left_negative_length():
    User.objects.bulk_create([
        User(username='fred@hogwarts.edu'),
        User(username='george@hogwarts.edu'),
        User(username='luna@hogwarts.edu'),
    ])

    assert list(
        User.objects
        .annotate(name=Left('username', -13))
        .order_by('id')
        .values_list('name', flat=True)
    ) == ['fred', 'george', 'luna']


@mark.django_db
def test_right_negative_length():
    User.objects.bulk_create([
        User(username='A01single-tube'),
        User(username='D06plate'),
        User(username='F08tube-rack'),
        User(username='H12plate'),
        User(username='P24plate'),
    ])

    assert list(
        User.objects
        .annotate(container=Right('username', -3))
        .order_by('id')
        .values_list('container', flat=True)
    ) == ['single-tube', 'plate', 'tube-rack', 'plate', 'plate']


@mark.django_db
@mark.parametrize(
    ('time_zone', 'offset'),
    (('America/Los_Angeles', '-08:00'), ('Asia/Kolkata', '+05:30'), ('UTC', '+00:00')),
)
def test_strftime_timezone_offset(
    monkeypatch: MonkeyPatch, settings: SettingsWrapper, time_zone: str, offset: str
):
    monkeypatch.setattr(
        'django_plugin_field_day.datetime',
        SimpleNamespace(now=lambda zone: datetime(2026, 2, 3, tzinfo=zone)),
    )
    settings.TIME_ZONE = time_zone
    User.objects.create(username='luna@hogwarts.edu')

    assert (
        User.objects
        .annotate(formatted=StrFTime(Value('2026-02-03 04:05:06.789'), '%Y-%m-%dT%H:%M:%f%z'))
        .values_list('formatted', flat=True)
        .first()
        == f'2026-02-03T04:05:06.789{offset}'
    )
