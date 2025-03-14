from django.contrib import admin
from django.forms import TextInput
from units.models import *
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site


# Remove Groups
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.unregister(Site)


class RepresentationsInline(admin.TabularInline):
    model = Representations
    fields = ('repsystem', 'status', 'checked')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '7'})},
    }


class UnitsAdmin(admin.ModelAdmin):
    """ systems table admin config """
    list_display = ('name', 'description', 'updated')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('unitsystem__name',)
    inlines = [RepresentationsInline,]


admin.site.register(Units, UnitsAdmin)
# admin.site.register(Representations)
