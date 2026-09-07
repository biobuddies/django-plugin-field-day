from typing import Final

import django.db.models.deletion
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps

from django_plugin_field_day.countries import COUNTRIES


def load_countries(apps: StateApps, _schema_editor: BaseDatabaseSchemaEditor) -> None:
    Country = apps.get_model('django_plugin_field_day', 'Country')
    Country.objects.bulk_create(Country(code=code, name=name) for code, name, _part_of in COUNTRIES)
    Country.objects.bulk_update(
        [Country(code=code, part_of_id=part_of) for code, _name, part_of in COUNTRIES if part_of],
        ['part_of'],
    )


def drop_countries(apps: StateApps, _schema_editor: BaseDatabaseSchemaEditor) -> None:
    countries = apps.get_model('django_plugin_field_day', 'Country').objects
    countries.update(part_of=None)  # release PROTECTed self-references before deleting
    countries.all().delete()


class Migration(migrations.Migration):
    initial = True

    dependencies: Final = []

    operations: Final = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                (
                    'part_of',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='parts',
                        to='django_plugin_field_day.country',
                    ),
                ),
            ],
        ),
        migrations.RunPython(load_countries, drop_countries),
    ]
