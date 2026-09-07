"""Regenerate django_plugin_field_day/countries.py from Chromium's libaddressinput.

The service at https://chromium-i18n.appspot.com/ssl-address/data lists ISO 3166-1 alpha-2
codes; each per-country document carries the display name (and, someday, the postal-code
regex we may add). Run: python scripts/fetch_countries.py
"""

import json
import logging
from pathlib import Path
from urllib.request import urlopen

logger = logging.getLogger(__name__)

DATA_URL = 'https://chromium-i18n.appspot.com/ssl-address/data'

# United States territories: Chromium lists them as USPS
# subdivisions without encoding sovereignty, so this curation excludes the independent Compact
# of Free Association states (FM, MH, PW) that USPS also serves.
PART_OF = {'AS': 'US', 'GU': 'US', 'MP': 'US', 'PR': 'US', 'UM': 'US', 'VI': 'US'}


def fetch(path: str) -> dict[str, str]:
    with urlopen(path, timeout=60) as response:  # noqa: S310
        return json.load(response)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    codes = fetch(DATA_URL)['countries'].split('~')
    logger.info('Fetching %d countries', len(codes))
    rows = ''.join(
        f'    {(code, fetch(f"{DATA_URL}/{code}")["name"], PART_OF.get(code))!r},\n'
        for code in codes
    )
    (
        Path(__file__).resolve().parent.parent / 'django_plugin_field_day' / 'countries.py'
    ).write_text(
        '"""ISO 3166-1 alpha-2 countries from Chromium libaddressinput; see '
        'scripts/fetch_countries.py."""\n\n'
        f'COUNTRIES = (\n{rows})\n'
    )


if __name__ == '__main__':
    main()
