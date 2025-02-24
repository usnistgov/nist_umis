from django.contrib import admin
from units.models import *


@admin.register(Domains)
class DomainsAdmin(admin.ModelAdmin):
    """ systems table admin config """
    list_display = ('id', 'title', 'type')
    ordering = ('title',)
    search_fields = ('title',)
