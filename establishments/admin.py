from django.contrib import admin

from .models import Establishment


class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'owner')
    search_fields = ('name', 'email', 'phone_number')
    list_filter = ('owner', 'happy_hour_start', 'happy_hour_end')

    fieldsets = (
        ('General Information', {'fields': ('name', 'email', 'owner')}),
        ('Address', {'fields': ('street_name', 'street_number', 'latitude', 'longitude')}),
        ('Details', {'fields': ('description', 'phone_number', 'logo', 'banner_image')}),
        ('Happy Hour', {'fields': ('happy_hour_start', 'happy_hour_end')}),
    )


admin.site.register(Establishment, EstablishmentAdmin)
