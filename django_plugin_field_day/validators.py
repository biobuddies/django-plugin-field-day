"""Reusable field validators for shipping addresses."""

from django.core.validators import RegexValidator

# Latin-1 printable only: space through tilde plus the upper printable range.
# Thermal label printers and the FedEx/UPS/DHL APIs choke on control characters,
# tabs, and most emoji, so reject anything outside this range.
validate_label_safe = RegexValidator(
    r'^[\x20-\x7e\xa0-\xff]*$', 'Only Latin-1 printable characters fit on a shipping label.'
)
