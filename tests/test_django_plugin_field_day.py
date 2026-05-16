"""Tests for django-plugin-field-day."""

import re

import pytest
from django.contrib.auth.models import User
from django.db.models.functions.datetime import Now
from django.test.client import Client
from django.test.utils import override_settings

from django_plugin_field_day import StrFTime


@pytest.mark.django_db
def test_index_page_200():
    response = Client().get('/')
    assert response.status_code == 200


@pytest.mark.django_db
@override_settings(TIME_ZONE='America/Los_Angeles')
def test_strftime_pacific_timezone_offset():
    User.objects.create_user('testuser')
    qs = User.objects.annotate(ts=StrFTime(Now(), '%Y-%m-%dT%H:%M:%f%z'))
    ts = qs.values_list('ts', flat=True).first()
    assert ts is not None
    m = re.search(r'([-+]\d{2}:\d{2}|Z)$', ts)
    assert m, f'timestamp missing ISO 8601 offset: {ts!r}'
    offset = m.group(1)
    assert offset != '+00:00', f'expected Pacific offset, got {offset!r}'
    assert offset in ('-07:00', '-08:00'), (
        f'expected Pacific offset (-07:00 or -08:00), got {offset!r}'
    )


@pytest.mark.django_db
@override_settings(TIME_ZONE='UTC')
def test_strftime_utc_timezone_offset():
    User.objects.create_user('testuser')
    qs = User.objects.annotate(ts=StrFTime(Now(), '%Y-%m-%dT%H:%M:%f%z'))
    ts = qs.values_list('ts', flat=True).first()
    assert ts is not None
    m = re.search(r'([-+]\d{2}:\d{2}|Z)$', ts)
    assert m, f'timestamp missing ISO 8601 offset: {ts!r}'
    offset = m.group(1)
    assert offset == '+00:00', f'expected +00:00 for UTC, got {offset!r}'


@pytest.mark.django_db
@override_settings(TIME_ZONE='Asia/Kolkata')
def test_strftime_india_timezone_offset():
    User.objects.create_user('testuser')
    qs = User.objects.annotate(ts=StrFTime(Now(), '%Y-%m-%dT%H:%M:%f%z'))
    ts = qs.values_list('ts', flat=True).first()
    assert ts is not None
    m = re.search(r'([-+]\d{2}:\d{2})$', ts)
    assert m, f'timestamp missing ISO 8601 offset: {ts!r}'
    assert m.group(1) == '+05:30', f'expected +05:30, got {m.group(1)!r}'
