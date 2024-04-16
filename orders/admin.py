from django.contrib import admin
from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'establishment', 'menu_item', 'order_date', 'status', 'quantity')
    list_filter = ('status', 'establishment', 'menu_item', 'user')
    search_fields = ('user__email', 'establishment__name', 'menu_item__name', 'status')
    date_hierarchy = 'order_date'
    readonly_fields = ('order_date', 'last_updated')
    fieldsets = (
        (None, {'fields': ('user', 'establishment', 'menu_item')}),
        ('Order Details', {'fields': ('quantity', 'status', 'order_date', 'last_updated')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user', 'establishment', 'menu_item')
        return self.readonly_fields


admin.site.register(Order, OrderAdmin)
