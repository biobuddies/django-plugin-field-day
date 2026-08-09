"""Tests for django-plugin-field-day."""

from django.contrib.auth.models import User
from django.db import NotSupportedError, connections
from django.db.models import Value
from django.db.models.functions import Now
from pytest import mark, raises
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
@mark.parametrize('time_zone', ('Africa/Freetown', 'UTC'))
@mark.parametrize(
    ('moment', 'expected'),
    (
        ('2026-01-23 04:05:06.789', '2026-01-23 04:05:06.789+00:00'),
        ('2026-07-23 04:05:06.789', '2026-07-23 04:05:06.789+00:00'),
    ),
)
def test_strftime_utc_offset(settings: SettingsWrapper, expected: str, moment: str, time_zone: str):
    settings.TIME_ZONE = time_zone
    User.objects.create(username='luna@hogwarts.edu')

    assert (
        User.objects
        .annotate(formatted=StrFTime(Value(moment), '%Y-%m-%d %H:%M:%f%z'))
        .values_list('formatted', flat=True)
        .first()
        == expected
    )


@mark.django_db
@mark.parametrize('time_zone', ('America/Los_Angeles', 'Asia/Kolkata', 'Europe/London'))
def test_strftime_raises_for_offset_timezone(settings: SettingsWrapper, time_zone: str):
    settings.TIME_ZONE = time_zone

    with raises(NotSupportedError, match='not supported yet'):
        list(
            User.objects.annotate(
                formatted=StrFTime(Value('2026-01-23 04:05:06.789'), '%H:%M%z')
            ).values_list('formatted', flat=True)
        )


@mark.django_db
@mark.parametrize(
    ('format_string', 'expected'),
    (
        ('%Y-%m-%d', '2026-01-23'),
        ('%z hours and minutes from UTC', '+00:00 hours and minutes from UTC'),
    ),
)
def test_strftime_renders_format_string(expected: str, format_string: str):
    User.objects.create(username='luna@hogwarts.edu')

    assert (
        User.objects
        .annotate(formatted=StrFTime(Value('2026-01-23 04:05:06.789'), format_string))
        .values_list('formatted', flat=True)
        .first()
        == expected
    )


def test_strftime_postgresql_receives_percent_z():
    sql, parameters = StrFTime(Value('2026-01-23 04:05:06.789'), '%Y-%m-%d %H:%M%z').as_sql(
        User.objects.all().query.get_compiler(using='default'), connections['default']
    )

    assert sql % tuple(parameters) == "STRFTIME('%Y-%m-%d %H:%M%z', 2026-01-23 04:05:06.789)"


def test_strftime_sqlite_receives_percent_percent_z():
    sql, parameters = StrFTime(Value('2026-01-23 04:05:06.789'), '%Y-%m-%d %H:%M%z').as_sqlite(
        User.objects.all().query.get_compiler(using='default'), connections['default']
    )

    assert sql % tuple(parameters) == (
        "REPLACE(STRFTIME('%Y-%m-%d %H:%M%%z', 2026-01-23 04:05:06.789), '%z', '+00:00')"
    )


@mark.django_db
def test_strftime_now_utc_offset():
    User.objects.create(username='luna@hogwarts.edu')

    assert (
        User.objects
        .annotate(formatted=StrFTime(Now(), '%Y-%m-%d %H:%M:%f%z'))
        .values_list('formatted', flat=True)
        .first()
        or ''
    ).endswith('+00:00')
