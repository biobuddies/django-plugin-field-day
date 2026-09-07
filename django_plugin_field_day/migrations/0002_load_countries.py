from typing import Final

from django.db import migrations

from django_plugin_field_day.countries import COUNTRIES


def load_countries(apps, schema_editor):
    Country = apps.get_model('django_plugin_field_day', 'Country')
    Country.objects.bulk_create(Country(code=code, name=name) for code, name, _part_of in COUNTRIES)
    Country.objects.bulk_update(
        [Country(code=code, part_of_id=part_of) for code, _name, part_of in COUNTRIES if part_of],
        ['part_of'],
    )


def drop_countries(apps, schema_editor):
    countries = apps.get_model('django_plugin_field_day', 'Country').objects
    countries.update(part_of=None)  # release PROTECTed self-references before deleting
    countries.all().delete()


class Migration(migrations.Migration):
    dependencies: Final = [('django_plugin_field_day', '0001_initial')]
    operations: Final = [migrations.RunPython(load_countries, drop_countries)]
