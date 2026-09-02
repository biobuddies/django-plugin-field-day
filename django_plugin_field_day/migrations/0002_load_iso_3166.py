"""Load the demo ISO 3166 countries and their subdivisions."""

from typing import Any, ClassVar

from django.db import migrations

COUNTRIES = {'US': 'United States', 'GB': 'United Kingdom', 'CN': 'China'}

# code suffix -> name. kind is uniform per country, so store it alongside the map.
SUBDIVISIONS = {
    'US': (
        'state',
        {
            'AL': 'Alabama',
            'AK': 'Alaska',
            'AZ': 'Arizona',
            'AR': 'Arkansas',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'HI': 'Hawaii',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'IA': 'Iowa',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'ME': 'Maine',
            'MD': 'Maryland',
            'MA': 'Massachusetts',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MS': 'Mississippi',
            'MO': 'Missouri',
            'MT': 'Montana',
            'NE': 'Nebraska',
            'NV': 'Nevada',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NY': 'New York',
            'NC': 'North Carolina',
            'ND': 'North Dakota',  # noqa: typos
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VT': 'Vermont',
            'VA': 'Virginia',
            'WA': 'Washington',
            'WV': 'West Virginia',
            'WI': 'Wisconsin',
            'WY': 'Wyoming',
            'DC': 'District of Columbia',
        },
    ),
    'GB': (
        'country',
        {'ENG': 'England', 'SCT': 'Scotland', 'WLS': 'Wales', 'NIR': 'Northern Ireland'},
    ),
    'CN': (
        'province',
        {
            '11': 'Beijing',
            '12': 'Tianjin',
            '13': 'Hebei',
            '14': 'Shanxi',
            '15': 'Nei Mongol',
            '21': 'Liaoning',
            '22': 'Jilin',
            '23': 'Heilongjiang',
            '31': 'Shanghai',
            '32': 'Jiangsu',
            '33': 'Zhejiang',
            '34': 'Anhui',
            '35': 'Fujian',
            '36': 'Jiangxi',
            '37': 'Shandong',
            '41': 'Henan',
            '42': 'Hubei',
            '43': 'Hunan',
            '44': 'Guangdong',
            '45': 'Guangxi',
            '46': 'Hainan',
            '50': 'Chongqing',
            '51': 'Sichuan',
            '52': 'Guizhou',
            '53': 'Yunnan',
            '54': 'Xizang',
            '61': 'Shaanxi',
            '62': 'Gansu',
            '63': 'Qinghai',
            '64': 'Ningxia',
            '65': 'Xinjiang',
        },
    ),
}


def load(apps: Any, schema_editor: Any) -> None:  # noqa: ARG001
    country_model = apps.get_model('django_plugin_field_day', 'Country')
    subdivision_model = apps.get_model('django_plugin_field_day', 'Subdivision')
    country_model.objects.bulk_create(
        country_model(code=code, name=name) for code, name in COUNTRIES.items()
    )
    subdivision_model.objects.bulk_create(
        subdivision_model(code=f'{country}-{suffix}', country_id=country, name=name, kind=kind)
        for country, (kind, members) in SUBDIVISIONS.items()
        for suffix, name in members.items()
    )


def unload(apps: Any, schema_editor: Any) -> None:  # noqa: ARG001
    apps.get_model('django_plugin_field_day', 'Subdivision').objects.all().delete()
    apps.get_model('django_plugin_field_day', 'Country').objects.all().delete()


class Migration(migrations.Migration):
    dependencies: ClassVar = [('django_plugin_field_day', '0001_initial')]
    operations: ClassVar = [migrations.RunPython(load, unload)]
