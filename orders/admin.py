from django.contrib import admin

from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu', 'beverage', 'order_date', 'status', 'quantity')
    list_filter = ('status', 'menu', 'beverage', 'user')
    search_fields = ('user__email', 'menu__establishment__name', 'beverage__name', 'status')
    date_hierarchy = 'order_date'
    readonly_fields = ('order_date', 'last_updated')
    fieldsets = (
        (None, {'fields': ('user', 'menu', 'beverage')}),
        ('Order Details', {'fields': ('quantity', 'status', 'order_date', 'last_updated')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user', 'menu', 'beverage')
        return self.readonly_fields


admin.site.register(Order, OrderAdmin)
