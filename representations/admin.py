from django.contrib import admin
from units.models import *


@admin.register(Representations)
class RepresentationsAdmin(admin.ModelAdmin):
    """ represetnations table admin config """
    list_display = ('unit__name', 'repsystem__name', 'strng__string')
    ordering = ('unit__name',)
    search_fields = ('unit__name',)
    list_filter = ('repsystem__name',)
    fields = ('repsystem__name', 'strng__string', 'status')


@admin.register(Strngs)
class StrngsAdmin(admin.ModelAdmin):
    list_display = ('name', 'string', 'status')
    ordering = ('name',)
    search_fields = ('name',)
    fields = ('name', 'string', 'status')
