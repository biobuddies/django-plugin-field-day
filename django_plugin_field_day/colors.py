"""Colors stored as 24-bit integers; #rrggbb is only how HTML and CSS write them."""

from re import fullmatch
from typing import Any, Self

from django.core.exceptions import ValidationError
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Field
from django.db.models.expressions import Expression
from django.forms import CharField as FormCharField
from django.forms import Field as FormField
from django.forms.widgets import Input, NumberInput

from django_plugin_field_day.fields import NumberField


class Color(int):
    """24-bit RGB number that parses and prints as lowercase #rrggbb."""

    def __new__(cls, value: int | str) -> Self:
        """Accept 0..0xffffff or #rrggbb in any letter case."""
        number = (
            int(value[1:], 16)
            if isinstance(value, str) and fullmatch('#[0-9a-fA-F]{6}', value)
            else value
        )
        if not isinstance(number, int) or isinstance(number, bool) or not 0 <= number <= 0xFFFFFF:
            raise ValidationError(
                '“%(value)s” is not a color like #1a2b3c.', code='invalid', params={'value': value}
            )
        return super().__new__(cls, number)

    def __str__(self) -> str:  # noqa: D105
        return f'#{self:06x}'


class ColorInput(Input):
    """Browsers only submit lowercase #rrggbb from the native color picker."""

    input_type = 'color'


class ColorFormField(FormCharField):
    """Cleans to Color so unchanged initial values compare equal."""

    widget = ColorInput

    def to_python(self, value: Any) -> Color | None:  # noqa: D102
        return None if value in self.empty_values else Color(value)


class ColorField(NumberField):
    """Database constraints, Python validation, and a native color input for 24-bit RGB colors.

    Stored as a plain integer; the Python value prints as #rrggbb.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, minimum=0, maximum=0xFFFFFF, **kwargs)

    def deconstruct(self) -> tuple:  # noqa: D102
        name, path, args, kwargs = super().deconstruct()
        del kwargs['minimum'], kwargs['maximum']
        return name, path, args, kwargs

    def formfield(self, **kwargs: Any) -> FormField | None:  # noqa: D102
        widget = kwargs.get('widget')
        if issubclass(widget if isinstance(widget, type) else type(widget), NumberInput):
            del kwargs['widget']  # ModelAdmin assumes IntegerField subclasses want a number
        defaults: dict[str, Any] = {'form_class': ColorFormField, **kwargs}
        return Field.formfield(self, **defaults)

    def from_db_value(
        self, value: int | None, _expression: Expression, _connection: BaseDatabaseWrapper
    ) -> Color | None:
        """Wrap stored integers."""
        return None if value is None else Color(value)

    def get_default(self) -> Color | None:  # noqa: D102
        return self.to_python(super().get_default())

    def get_prep_value(self, value: Any) -> int | None:  # noqa: D102
        return None if value is None else int(Color(value))

    def to_python(self, value: Any) -> Color | None:  # noqa: D102
        return None if value is None else Color(value)
