"""Regenerate django_plugin_field_day/countries.py from Chromium libaddressinput.

The index at https://chromium-i18n.appspot.com/ssl-address/data lists ISO 3166-1 alpha-2 codes;
each per-country document carries the display name and, for many, the ISO 3166-2 subdivisions in
parallel sub_isoids/sub_names arrays. One throttled async pass fetches every document once and
writes both the COUNTRIES table and the REGIONS map. Run: python scripts/fetch_countries.py
"""

import asyncio
from pathlib import Path

from aiohttp import ClientSession, TCPConnector

DATA = Path(__file__).resolve().parent.parent / 'django_plugin_field_day'
DATA_URL = 'https://chromium-i18n.appspot.com/ssl-address/data'

# https://trevmex.com/post/826439929093636096/the-us-is-more-than-just-the-us-according-to
# TODO add more https://en.wikipedia.org/wiki/ISO_3166-2#Subdivisions_included_in_ISO_3166-1
TERRITORIES = {'US': ('AS', 'GU', 'MP', 'PR', 'UM', 'VI')}


async def main() -> None:
    # Eight-way throttle: polite to the server and dodges proxy EOFs seen at full fan-out.
    async with ClientSession(connector=TCPConnector(limit=8)) as session:

        async def fetch(url: str) -> dict[str, str]:
            async with session.get(url) as response:
                return await response.json(content_type=None)

        documents = {
            document['key']: document
            for document in await asyncio.gather(
                *(
                    fetch(f'{DATA_URL}/{code}')
                    for code in (await fetch(DATA_URL))['countries'].split('~')
                )
            )
        }

    part_of = {code: sovereign for sovereign, codes in TERRITORIES.items() for code in codes}
    regions = {
        country: dict(
            sorted(
                (isoid, name)
                for isoid, name in zip(
                    documents[country].get('sub_isoids', '').split('~'),
                    documents[country].get('sub_names', '').split('~'),
                    strict=True,
                )
                if isoid
            )
        )
        for country in ('US', *TERRITORIES['US'])  # TODO expand in waves
    }
    (DATA / 'countries.py').write_text(
        '"""ISO 3166 countries and subdivisions from Chromium libaddressinput; see '
        'fetch_countries.py."""\n\n'
        'COUNTRIES = (\n'
        + ''.join(
            f'    {(code, document["name"], part_of.get(code))!r},\n'
            for code, document in documents.items()
        )
        + ')\n\n'
        'REGIONS = {\n'
        + ''.join(
            f'    {country!r}: {{\n'
            + ''.join(f'        {suffix!r}: {name!r},\n' for suffix, name in members.items())
            + '    },\n'
            for country, members in regions.items()
            if members
        )
        + '}\n'
    )


if __name__ == '__main__':
    asyncio.run(main())
