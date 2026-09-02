"""Form binding for the concrete Address model."""

from typing import Any

from django.forms import ModelForm

from django_plugin_field_day.models import Address


class AddressForm(ModelForm):
    """Normalize input before the model constraints run.

    Collapse internal whitespace and upper-case the coded fields so the
    country-specific postal checks see canonical values.
    """

    class Meta:
        """Bind every Address field."""

        model = Address
        fields = (
            'recipient',
            'country',
            'street1',
            'street2',
            'street3',
            'city',
            'subdivision',
            'postal_code',
        )

    def clean(self) -> dict[str, Any]:
        """Canonicalize whitespace and postal-code casing."""
        super().clean()
        cleaned = self.cleaned_data
        for line in ('recipient', 'street1', 'street2', 'street3', 'city'):
            value = cleaned.get(line)
            if value:
                cleaned[line] = ' '.join(value.split())
        if cleaned.get('postal_code'):
            cleaned['postal_code'] = cleaned['postal_code'].upper()
        return cleaned
