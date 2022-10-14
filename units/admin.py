from django.contrib import admin
from units.models import *


# Register your models here.
@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    """ systems table admin config """
    list_display = ('id', 'name', 'quantitykind', 'unitsystem')
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(Domains)
class DomainsAdmin(admin.ModelAdmin):
    """ systems table admin config """
    list_display = ('id', 'title', 'type')
    ordering = ('title',)
    search_fields = ('title',)
