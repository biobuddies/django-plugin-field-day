"""
Fields with consistent checks at every level.

1. Database CheckConstraints
2. Python validators
3. HTML5 constraint validation attributes
   https://developer.mozilla.org/en-US/docs/Web/HTML/Constraint_validation
"""

from collections.abc import Iterator
from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CheckConstraint, Field, IntegerField, Model, Q
from django.forms import Field as FormField


class CheckedMixin(Field):
    """Mirrors a field's rules as named database CheckConstraints."""

    def checks(self, name: str) -> Iterator[tuple[str, Q]]:
        """Yield the label and condition of each constraint."""
        raise NotImplementedError

    def contribute_to_class(self, cls: type[Model], name: str, private_only: bool = False) -> None:  # noqa: FBT002
        """Set table constraints."""
        super().contribute_to_class(cls, name, private_only=private_only)

        if cls.__module__ == '__fake__':
            return  # Avoid duplicate constraints when migrating

        # Ensure ModelState.from_model() considers constraints
        cls._meta.original_attrs['constraints'] = cls._meta.original_attrs.get('constraints', [])
        cls._meta.constraints = [
            *cls._meta.constraints,
            *(
                CheckConstraint(condition=condition, name=f'{cls._meta.db_table}.{name} {label}')
                for label, condition in self.checks(name)
            ),
        ]


class NumberField(CheckedMixin, IntegerField):
    """Integer from minimum to maximum inclusive, in the smallest database type that fits."""

    def __init__(
        self, *args: Any, minimum: int | None = None, maximum: int | None = None, **kwargs: Any
    ) -> None:
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError(f'minimum {minimum} exceeds maximum {maximum}')
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(*args, **kwargs)
        if minimum is not None:
            self.validators.append(MinValueValidator(minimum))
        if maximum is not None:
            self.validators.append(MaxValueValidator(maximum))

    def checks(self, name: str) -> Iterator[tuple[str, Q]]:  # noqa: D102
        if self.minimum is not None:
            yield f'>= {self.minimum}', Q(**{f'{name}__gte': self.minimum})
        if self.maximum is not None:
            yield f'<= {self.maximum}', Q(**{f'{name}__lte': self.maximum})

    def deconstruct(self) -> tuple:  # noqa: D102
        name, path, args, kwargs = super().deconstruct()
        if self.minimum is not None:
            kwargs['minimum'] = self.minimum
        if self.maximum is not None:
            kwargs['maximum'] = self.maximum
        return name, path, args, kwargs

    def formfield(self, **kwargs: Any) -> FormField | None:  # noqa: D102
        defaults: dict[str, Any] = {'min_value': self.minimum, 'max_value': self.maximum, **kwargs}
        return super().formfield(**defaults)

    def get_internal_type(self) -> str:  # noqa: D102
        low = -(2**31) if self.minimum is None else self.minimum
        high = 2**31 - 1 if self.maximum is None else self.maximum
        return next(
            (
                kind
                for bits, kind in ((16, 'SmallIntegerField'), (32, 'IntegerField'))
                if -(2 ** (bits - 1)) <= low and high < 2 ** (bits - 1)
            ),
            'BigIntegerField',
        )
