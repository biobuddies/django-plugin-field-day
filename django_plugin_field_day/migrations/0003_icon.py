from typing import Final

from django.db import migrations, models

import django_plugin_field_day.colors
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
                ('foreground', django_plugin_field_day.colors.ColorField(default='#000000')),
                ('background', django_plugin_field_day.colors.ColorField(default='#ffffff')),
                ('letters', django_plugin_field_day.fields.StringField(regex='.{0,4}')),
                ('svg', django_plugin_field_day.fields.StringField(regex='.{0,200}')),
            ],
            options={
                'constraints': [
                    models.CheckConstraint(
                        condition=models.Q(('foreground__gte', 0)),
                        name='django_plugin_field_day_icon.foreground >= 0',
                    ),
                    models.CheckConstraint(
                        condition=models.Q(('foreground__lte', 16777215)),
                        name='django_plugin_field_day_icon.foreground <= 16777215',
                    ),
                    models.CheckConstraint(
                        condition=models.Q(('background__gte', 0)),
                        name='django_plugin_field_day_icon.background >= 0',
                    ),
                    models.CheckConstraint(
                        condition=models.Q(('background__lte', 16777215)),
                        name='django_plugin_field_day_icon.background <= 16777215',
                    ),
                    models.CheckConstraint(
                        condition=models.Q(('letters__regex', '^(.{0,4})$')),
                        name='django_plugin_field_day_icon.letters matches regex',
                    ),
                    models.CheckConstraint(
                        condition=models.Q(('svg__regex', '^(.{0,200})$')),
                        name='django_plugin_field_day_icon.svg matches regex',
                    ),
                ]
            },
        )
    ]
