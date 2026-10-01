from typing import Final

from django.db import migrations, models

import django_plugin_field_day.fields


class Migration(migrations.Migration):
    dependencies: Final = [('django_plugin_field_day', '0003_icon')]

    operations: Final = [
        migrations.AddField(
            model_name='icon',
            name='background',
            field=django_plugin_field_day.fields.CheckedColorField(default='#ffffff'),
        ),
        migrations.AddField(
            model_name='icon',
            name='foreground',
            field=django_plugin_field_day.fields.CheckedColorField(default='#000000'),
        ),
        migrations.AddConstraint(
            model_name='icon',
            constraint=models.CheckConstraint(
                condition=models.Q(('foreground__gte', 0)),
                name='django_plugin_field_day_icon.foreground >= 0',
            ),
        ),
        migrations.AddConstraint(
            model_name='icon',
            constraint=models.CheckConstraint(
                condition=models.Q(('foreground__lte', 16777215)),
                name='django_plugin_field_day_icon.foreground <= 16777215',
            ),
        ),
        migrations.AddConstraint(
            model_name='icon',
            constraint=models.CheckConstraint(
                condition=models.Q(('background__gte', 0)),
                name='django_plugin_field_day_icon.background >= 0',
            ),
        ),
        migrations.AddConstraint(
            model_name='icon',
            constraint=models.CheckConstraint(
                condition=models.Q(('background__lte', 16777215)),
                name='django_plugin_field_day_icon.background <= 16777215',
            ),
        ),
    ]
