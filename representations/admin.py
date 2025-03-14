from django.contrib import admin, messages
from django.utils.translation import ngettext
from units.models import Representations, Strngs


@admin.register(Representations)
class RepresentationsAdmin(admin.ModelAdmin):
    """ represetnations table admin config """
    list_display = ('unit__name', 'repsystem__name', 'strng__string')
    ordering = ('unit__name',)
    search_fields = ('unit__name',)
    list_filter = ('repsystem__name',)
    fields = ('repsystem__name', 'strng__string', 'status')



    @admin.action(description="Check a representation on Wikidata")
    def wd_check_action(self, request, queryset):
        pass
        # updated=queryset.update(wd_check=True)
        # self.message_user(
        #     request,
        #     ngettext(
        #         "%d story was successfully marked as published.",
        #         "%d stories were successfully marked as published.",
        #         updated,
        #     )
        #     % updated,
        #     messages.SUCCESS,
        # )


@admin.register(Strngs)
class StrngsAdmin(admin.ModelAdmin):
    list_display = ('name', 'string', 'status')
    ordering = ('name',)
    search_fields = ('name',)
    fields = ('name', 'string', 'status')
