from typing import Final

from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps

from django_plugin_field_day.countries import REGIONS


def load_regions(apps: StateApps, _schema_editor: BaseDatabaseSchemaEditor) -> None:
    Region = apps.get_model('django_plugin_field_day', 'Region')
    Region.objects.bulk_create(
        Region(code=f'{country}-{suffix}', name=name)
        for country, members in REGIONS.items()
        for suffix, name in members.items()
    )


def drop_regions(apps: StateApps, _schema_editor: BaseDatabaseSchemaEditor) -> None:
    apps.get_model('django_plugin_field_day', 'Region').objects.all().delete()


class Migration(migrations.Migration):
    dependencies: Final = [('django_plugin_field_day', '0001_country')]

    operations: Final = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('code', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.RunPython(load_regions, drop_regions),
    ]
