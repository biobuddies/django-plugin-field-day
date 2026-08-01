from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import djp
from django.db.models import CharField, Func, Value
from django.db.models.expressions import Expression
from django.db.models.functions.text import Left as DjangoLeft
from django.db.models.functions.text import Length, Substr
from django.db.models.functions.text import Right as DjangoRight


class Left(DjangoLeft):
    """Returns the first length characters of the given text field or expression.

    A negative length returns all but the last -length characters.
    """

    def __init__(
        self, expression: str | Expression, length: int | Expression, **extra: Any
    ) -> None:
        # Skip DjangoLeft.__init__, which raises ValueError for length < 1
        Func.__init__(self, expression, length, **extra)

    def get_substr(self) -> Substr:  # noqa: D102
        length = self.source_expressions[1]
        return (
            Substr(
                self.source_expressions[0],
                Value(1),
                Length(self.source_expressions[0]) + length.value,
            )
            if isinstance(length, Value) and length.value < 0
            else super().get_substr()
        )


class Right(Left, DjangoRight):
    """Returns the last length characters of the given text field or expression.

    A negative length returns all but the first -length characters.
    """

    def get_substr(self) -> Substr:  # noqa: D102
        length = self.source_expressions[1]
        return (
            Substr(self.source_expressions[0], Value(1) - length.value)
            if isinstance(length, Value) and length.value < 0
            else super().get_substr()
        )


class StrFTime(Func):
    """Format a datetime expression with SQL STRFTIME, supporting %z timezone offset from UTC."""

    function = 'STRFTIME'
    output_field = CharField()  # pyrefly: ignore[bad-override]

    def __init__(self, expression: Expression, format_string: str, **extra: Any) -> None:
        self.format_string = format_string
        escaped = format_string.replace('%', '%%%%')
        self.template = f"%(function)s('{escaped}', %(expressions)s)"
        super().__init__(expression, **extra)

    def as_sqlite(self, compiler, connection):  # noqa: ANN001, ANN201  # pyrefly: ignore[bad-override]
        """Append %z as a literal, since SQLite has no timezone database.

        The literal holds the settings.TIME_ZONE offset in effect when the SQL is generated,
        not the offset at the formatted datetime.
        """
        from django.conf import settings  # noqa: PLC0415

        format_string = self.format_string
        tz_literal = ''
        if '%z' in format_string:
            format_string = format_string.replace('%z', '')
            timezone_offset = datetime.now(ZoneInfo(settings.TIME_ZONE)).strftime('%z')
            tz_literal = (
                f'{timezone_offset[:3]}:{timezone_offset[3:]}' if timezone_offset else '+00:00'
            )
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
