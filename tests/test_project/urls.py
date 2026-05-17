"""Test project URL configuration."""

import djp
from django.http import HttpResponse
from django.urls import path

urlpatterns = [*[path('', lambda _request: HttpResponse('Hello world'))], *djp.urlpatterns()]
