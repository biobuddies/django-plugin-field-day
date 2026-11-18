"""Reference tables and a validated address for well-validated address fields."""

from django.core.validators import RegexValidator
from django.db.models import PROTECT, CharField, CheckConstraint, ForeignKey, Model, Q

from django_plugin_field_day import Left

# Latin-1 printable only; thermal label printers and the carrier APIs choke on control characters.
label_safe = RegexValidator(
    r'^[\x20-\x7e\xa0-\xff]*$', 'Only Latin-1 printable characters fit on a shipping label.'
)


class Country(Model):
    """ISO 3166-1 alpha-2 country, naturally keyed by its two-letter code.

    part_of links a dependent territory to its sovereign, so US-associated codes like PR and
    VI resolve to US; postal-code regexes and similar fields may join it later.
    """

    code = CharField(max_length=2, primary_key=True)
    name = CharField(max_length=50)
    part_of = ForeignKey('self', PROTECT, blank=True, null=True, related_name='parts')

    def __str__(self) -> str:  # noqa: D105
        return f'{self.code} {self.name}'


class Region(Model):
    """ISO 3166-2 subdivision, naturally keyed by the qualified code ('US-CA').

    The country is LEFT(code, 2); a ForeignKey to Country is left off for now. A directly
    administered place needs no special casing: Singapore simply has no Region, while Shanghai
    can take a synthetic eponymous row (code 'CN-SH', name 'Shanghai') should an address there
    want a non-null region.
    """

    code = CharField(primary_key=True, max_length=6)
    name = CharField(max_length=50)

    def __str__(self) -> str:  # noqa: D105
        return f'{self.code} {self.name}'


class Address(Model):
    """Print-ready address whose columns become CHECK constraints.

    Each street line is sized to the 35-character floor FedEx and UPS enforce.
    """

    recipient = CharField(max_length=35, validators=[label_safe])
    country = ForeignKey(Country, PROTECT)
    street1 = CharField(max_length=35, validators=[label_safe])
    street2 = CharField(max_length=35, blank=True, default='', validators=[label_safe])
    street3 = CharField(max_length=35, blank=True, default='', validators=[label_safe])
    city = CharField(max_length=30, validators=[label_safe])
    region = ForeignKey(Region, PROTECT, blank=True, null=True)
    postal_code = CharField(max_length=10)

    class Meta:  # noqa: D106
        constraints = (
            CheckConstraint(
                condition=~Q(recipient__regex=r'[\n\r\t]')
                & ~Q(street1__regex=r'[\n\r\t]')
                & ~Q(street2__regex=r'[\n\r\t]')
                & ~Q(street3__regex=r'[\n\r\t]')
                & ~Q(city__regex=r'[\n\r\t]'),
                name='address_no_control_characters',
            ),
            CheckConstraint(
                condition=Q(recipient__regex=r'\S')
                & Q(street1__regex=r'\S')
                & Q(city__regex=r'\S'),
                name='address_required_lines_present',
            ),
            CheckConstraint(
                condition=(Q(street2='') | Q(street2__regex=r'\S'))
                & (Q(street3='') | Q(street3__regex=r'\S')),
                name='address_optional_lines_not_blank',
            ),
            CheckConstraint(
                condition=~Q(street2='') | Q(street3=''), name='address_street_lines_no_gap'
            ),
            CheckConstraint(
                condition=Q(region__isnull=True) | Q(country=Left('region', 2)),
                name='address_region_in_country',
            ),
        )

    def __str__(self) -> str:  # noqa: D105
        return f'{self.recipient}, {self.city} {self.postal_code} {self.country_id}'
