""" admin setup for systems """
from django.contrib import admin
from constants.models import *


@admin.register(Constants)
class ConstantsAdmin(admin.ModelAdmin):
    """ systems table admin config """
    list_display = ('id', 'name')
    ordering = ('name',)
    search_fields = ('name',)
