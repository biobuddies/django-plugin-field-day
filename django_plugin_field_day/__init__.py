from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import djp
from django.db.models import CharField, Func, Value
from django.db.models.expressions import Expression
from django.db.models.functions.text import Length, Substr


def _format_tz_offset(tz_name: str) -> str:
    """Return ISO 8601 offset like '-07:00' for a timezone name."""
    offset_str = datetime.now(ZoneInfo(tz_name)).strftime('%z')
    if not offset_str:
        return '+00:00'
    return f'{offset_str[:3]}:{offset_str[3:]}'


class Left(Func):
    """https://code.djangoproject.com/ticket/36845."""

    function = 'LEFT'
    arity = 2
    output_field = CharField()  # pyrefly: ignore[bad-override]

    def __init__(self, expression: Expression, length: int | Expression, **extra: Any) -> None:
        super().__init__(expression, length, **extra)

    def get_substr(self) -> Substr:  # noqa: D102
        length = self.source_expressions[1]
        if not hasattr(length, 'resolve_expression') and length < 0:  # pyrefly: ignore[unsupported-operation]
            adjusted = Length(self.source_expressions[0]) + length
            return Substr(self.source_expressions[0], Value(1), adjusted)
        return Substr(self.source_expressions[0], Value(1), self.source_expressions[1])

    def as_oracle(self, compiler, connection, **extra_context):  # noqa: ANN001, ANN003, ANN201, D102
        return self.get_substr().as_oracle(compiler, connection, **extra_context)

    def as_sqlite(self, compiler, connection, **extra_context):  # noqa: ANN001, ANN003, ANN201, D102
        return self.get_substr().as_sqlite(compiler, connection, **extra_context)


class Right(Left):
    function = 'RIGHT'

    def get_substr(self) -> Substr:  # noqa: D102
        length = self.source_expressions[1]
        if not hasattr(length, 'resolve_expression') and length < 0:  # pyrefly: ignore[unsupported-operation]
            return Substr(self.source_expressions[0], Value(1) - length)
        return Substr(
            self.source_expressions[0],
            self.source_expressions[1] * Value(-1),
            self.source_expressions[1],
        )


class StrFTime(Func):
    function = 'STRFTIME'
    output_field = CharField()  # pyrefly: ignore[bad-override]

    def __init__(self, expression: Expression, format_string: str, **extra: Any) -> None:
        self.format_string = format_string
        escaped = format_string.replace('%', '%%%%')
        self.template = f"%(function)s('{escaped}', %(expressions)s)"
        super().__init__(expression, **extra)

    def as_sqlite(self, compiler, connection):  # noqa: ANN001, ANN201, D102  # pyrefly: ignore[bad-override]
        from django.conf import settings  # noqa: PLC0415

        format_string = self.format_string
        tz_literal = ''
        if '%z' in format_string:
            format_string = format_string.replace('%z', '')
            tz_literal = _format_tz_offset(settings.TIME_ZONE)
        escaped = format_string.replace('%', '%%%%')
        template = f"%(function)s('{escaped}', %(expressions)s)"
        if tz_literal:
            template += f" || '{tz_literal}'"
        return self.as_sql(compiler, connection, template=template)


@djp.hookimpl
def installed_apps() -> list:
    # A list of app strings to add to INSTALLED_APPS:
    return []


@djp.hookimpl
def urlpatterns() -> list:
    # A list of URL patterns to add to urlpatterns:
    return []


@djp.hookimpl
def settings(current_settings: Any) -> None:
    # Make changes to the Django settings.py globals here
    pass


@djp.hookimpl
def middleware() -> list:
    # A list of middleware class strings to add to MIDDLEWARE:
    # Wrap strings in djp.Before("middleware_class_name") or
    # djp.After("middleware_class_name") to specify before or after
    return []
