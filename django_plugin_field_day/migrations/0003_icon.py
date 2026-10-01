from typing import Final

from django.db import migrations, models

import django_plugin_field_day.fields


class Migration(migrations.Migration):
    dependencies: Final = [('django_plugin_field_day', '0002_region')]

    operations: Final = [
        migrations.CreateModel(
            name='Icon',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'letters',
                    django_plugin_field_day.fields.CheckedCharField(
                        blank=True, max_length=4, min_length=0
                    ),
                ),
                (
                    'svg',
                    django_plugin_field_day.fields.CheckedCharField(
                        blank=True, max_length=200, min_length=0
                    ),
                ),
            ],
            options={
                'constraints': [
                    models.CheckConstraint(
                        condition=models.Q(('letters__length__lte', 4)),
                        name='len(django_plugin_field_day_icon.letters) <= 4',
                    ),
                    models.CheckConstraint(
                        condition=models.Q(('svg__length__lte', 200)),
                        name='len(django_plugin_field_day_icon.svg) <= 200',
                    ),
                ]
            },
        )
    ]
