from django.contrib import admin
from units.models import Units


# Register your models here.
@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    """ systems table admin config """
