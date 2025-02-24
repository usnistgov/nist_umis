from django.contrib import admin
from units.models import *


@admin.register(Unitsystems)
class UnitsystemsAdmin(admin.ModelAdmin):
    """ systems table admin config """
    list_display = ('name', 'description', 'updated')
    ordering = ('name',)
    search_fields = ('name',)
