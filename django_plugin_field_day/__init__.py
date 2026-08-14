from typing import Any

import djp
from django.db import NotSupportedError
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


# zoneinfo names that render +00:00 in every month of every year, so %z can hardcode +00:00
UTC_TIME_ZONES = frozenset({
    'Africa/Abidjan',
    'Africa/Accra',
    'Africa/Bamako',
    'Africa/Banjul',
    'Africa/Bissau',
    'Africa/Conakry',
    'Africa/Dakar',
    'Africa/Freetown',
    'Africa/Lome',
    'Africa/Monrovia',
    'Africa/Nouakchott',
    'Africa/Ouagadougou',
    'Africa/Sao_Tome',
    'Africa/Timbuktu',
    'America/Danmarkshavn',
    'Atlantic/Reykjavik',
    'Atlantic/St_Helena',
    'Etc/GMT',
    'Etc/GMT+0',
    'Etc/GMT-0',
    'Etc/GMT0',
    'Etc/Greenwich',
    'Etc/UCT',
    'Etc/UTC',
    'Etc/Universal',
    'Etc/Zulu',
    'Factory',
    'GMT',
    'GMT+0',
    'GMT-0',
    'GMT0',
    'Greenwich',
    'Iceland',
    'UCT',
    'UTC',
    'Universal',
    'Zulu',
})


class StrFTime(Func):
    """Format a datetime expression with SQL STRFTIME, supporting %z timezone offset from UTC."""

    function = 'STRFTIME'
    output_field = CharField()  # pyrefly: ignore[bad-override]

    def __init__(self, expression: Expression, format_string: str, **extra: Any) -> None:
        self.format_string = format_string
        self.template = "%(function)s('{}', %(expressions)s)".format(
            format_string.replace('%', '%%%%')
        )
        super().__init__(expression, **extra)

    def as_sqlite(self, compiler, connection):  # noqa: ANN001, ANN201  # pyrefly: ignore[bad-override]
        """Substitute %z with +00:00 in place, because SQLite formats the stored UTC value.

        STRFTIME returns NULL for %z, so %%z carries it through as a literal for REPLACE.
        Converting to an offset timezone would need the timezone database SQLite lacks, so
        %z demands a TIME_ZONE that stays on UTC year round, such as UTC or Africa/Freetown.
        """
        from django.conf import settings  # noqa: PLC0415

        if '%z' in self.format_string and settings.TIME_ZONE not in UTC_TIME_ZONES:
            raise NotSupportedError(
                f'%z on SQLite when TIME_ZONE={settings.TIME_ZONE} not supported yet'
            )
        return self.as_sql(
            compiler,
            connection,
            template="REPLACE({}, '%%%%z', '+00:00')".format(
                self.template.replace('%%%%z', '%%%%%%%%z')
            ),
        )


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
