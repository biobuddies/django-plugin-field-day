"""Admin forms inherit HTML5 constraints from the model fields."""

from django.contrib.admin import ModelAdmin, register

from django_plugin_field_day.models import Icon


@register(Icon)
class IconAdmin(ModelAdmin):
    list_display = ('letters', 'svg')
