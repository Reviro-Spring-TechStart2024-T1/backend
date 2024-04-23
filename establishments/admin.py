from django.contrib import admin

from .models import Establishment


class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'owner', 'happy_hour_start', 'happy_hour_end')
    list_filter = ('owner',)
    search_fields = ('name', 'email', 'phone_number')
    fieldsets = (
        (None, {'fields': ('owner', 'name', 'email')}),
        ('Location', {'fields': ('latitude', 'longitude')}),
        ('Contact', {'fields': ('phone_number', 'avatar')}),
        ('Description', {'fields': ('description', 'happy_hour_start', 'happy_hour_end')}),
    )


admin.site.register(Establishment, EstablishmentAdmin)
