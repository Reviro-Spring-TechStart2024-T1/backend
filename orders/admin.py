from django.contrib import admin

from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'establishment', 'beverage', 'order_date', 'status', 'quantity')
    list_filter = ('status', 'establishment', 'beverage', 'user')
    search_fields = ('user__email', 'establishment__name', 'beverage__name', 'status')
    date_hierarchy = 'order_date'
    readonly_fields = ('order_date', 'last_updated')
    fieldsets = (
        (None, {'fields': ('user', 'establishment', 'beverage')}),
        ('Order Details', {'fields': ('quantity', 'status', 'order_date', 'last_updated')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user', 'establishment', 'beverage')
        return self.readonly_fields


admin.site.register(Order, OrderAdmin)
