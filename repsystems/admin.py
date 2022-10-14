""" admin setup for repsystems """
from django.contrib import admin
from units.models import *


@admin.register(Repsystems)
class RepsystemsAdmin(admin.ModelAdmin):
    """ repsystems table admin config """
    list_display = ('id', 'name', 'abbrev', 'version')
    ordering = ('name',)
    search_fields = ('name',)
