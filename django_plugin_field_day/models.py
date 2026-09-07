"""Reference tables for well-validated address fields."""

from django.db.models import PROTECT, CharField, ForeignKey, Model


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
