"""Validated, print-ready postal address fields with database-enforced rules."""

from typing import ClassVar

from django.db.models import CASCADE, PROTECT, CharField, CheckConstraint, ForeignKey, Model, Q

from django_plugin_field_day import Left
from django_plugin_field_day.validators import validate_label_safe


class Country(Model):
    """ISO 3166-1 alpha-2 country. Load every country to scale beyond the demo set."""

    code = CharField(primary_key=True, max_length=2)
    name = CharField(max_length=75)

    class Meta:
        """Pluralize the admin label correctly."""

        verbose_name_plural = 'countries'

    def __str__(self) -> str:
        """Return the alpha-2 code."""
        return self.code


class Subdivision(Model):
    """ISO 3166-2 subdivision.

    The code embeds its country ('US-CA'), so a single CHECK ties an address to a
    region in its own country without a cross-table lookup.
    """

    code = CharField(primary_key=True, max_length=6)
    country = ForeignKey(Country, on_delete=CASCADE, related_name='subdivisions')
    name = CharField(max_length=75)
    kind = CharField(max_length=20)

    def __str__(self) -> str:
        """Return the ISO 3166-2 code."""
        return self.code


# Per-country demo rules. All-caps letter classes keep the DB check case-blind so a
# raw INSERT is validated even when the form has not upper-cased first.
_POSTAL = {
    'US': r'^\d{5}(-\d{4})?$',
    'GB': r'^[A-Za-z]{1,2}\d[A-Za-z\d]? ?\d[A-Za-z]{2}$',
    'CN': r'^\d{6}$',
}
_SUBDIVISION_REQUIRED = ('US', 'CN')


class AbstractPostalAddress(Model):
    """Print-ready address as separate columns so most rules become CHECK constraints.

    Sized to the FedEx/UPS floor of 35 characters per street line; DHL tolerates 45.
    Optional street lines default to the empty string rather than NULL.
    """

    recipient = CharField(max_length=35, validators=[validate_label_safe])
    country = ForeignKey(Country, on_delete=PROTECT)
    street1 = CharField(max_length=35, validators=[validate_label_safe])
    street2 = CharField(max_length=35, blank=True, default='', validators=[validate_label_safe])
    street3 = CharField(max_length=35, blank=True, default='', validators=[validate_label_safe])
    city = CharField(max_length=30, validators=[validate_label_safe])
    subdivision = ForeignKey(Subdivision, on_delete=PROTECT, null=True, blank=True)
    postal_code = CharField(max_length=10)

    class Meta:
        """Database CHECK constraints shared by every concrete address."""

        abstract = True
        constraints: ClassVar = [
            CheckConstraint(
                condition=(
                    ~Q(recipient__regex=r'[\n\r\t]')
                    & ~Q(street1__regex=r'[\n\r\t]')
                    & ~Q(street2__regex=r'[\n\r\t]')
                    & ~Q(street3__regex=r'[\n\r\t]')
                    & ~Q(city__regex=r'[\n\r\t]')
                ),
                name='%(class)s_no_control_characters',
            ),
            CheckConstraint(
                condition=(
                    Q(recipient__regex=r'\S') & Q(street1__regex=r'\S') & Q(city__regex=r'\S')
                ),
                name='%(class)s_required_lines_present',
            ),
            CheckConstraint(
                condition=(
                    (Q(street2='') | Q(street2__regex=r'\S'))
                    & (Q(street3='') | Q(street3__regex=r'\S'))
                ),
                name='%(class)s_optional_lines_not_blank',
            ),
            CheckConstraint(
                condition=~Q(street2='') | Q(street3=''), name='%(class)s_street_lines_no_gap'
            ),
            CheckConstraint(
                condition=Q(subdivision__isnull=True) | Q(country=Left('subdivision', 2)),
                name='%(class)s_subdivision_in_country',
            ),
            CheckConstraint(
                condition=Q(subdivision__isnull=False) | ~Q(country__in=_SUBDIVISION_REQUIRED),
                name='%(class)s_subdivision_required_by_country',
            ),
            CheckConstraint(
                condition=(
                    Q(country='US', postal_code__regex=_POSTAL['US'])
                    | Q(country='GB', postal_code__regex=_POSTAL['GB'])
                    | Q(country='CN', postal_code__regex=_POSTAL['CN'])
                ),
                name='%(class)s_postal_code_matches_country',
            ),
        ]


class Address(AbstractPostalAddress):
    """Concrete demo table exercising AbstractPostalAddress."""

    def __str__(self) -> str:
        """Summarize the address on one line."""
        return f'{self.recipient}, {self.city} {self.postal_code} {self.country_id}'
