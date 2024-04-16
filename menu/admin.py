from django.contrib import admin
from .models import ItemCategory, MenuItem, Menu
from django.utils.safestring import mark_safe


class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(ItemCategory, ItemCategoryAdmin)


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_category', 'price', 'availability_status', 'happy_hour_start', 'happy_hour_end', 'menu')
    list_filter = ('availability_status', 'item_category', 'menu')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {'fields': ('menu', 'name', 'item_category', 'price', 'availability_status')}),
        ('Description and Timing', {'fields': ('description', 'happy_hour_start', 'happy_hour_end')}),
    )


admin.site.register(MenuItem, MenuItemAdmin)


class MenuAdmin(admin.ModelAdmin):
    list_display = ('establishment', 'created_at', 'updated_at', 'qr_code_preview')
    readonly_fields = ('created_at', 'updated_at', 'qr_code_preview')
    fieldsets = (
        (None, {'fields': ('establishment',)}),
        ('QR Code', {'fields': ('qr_code_image', 'qr_code_preview')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def qr_code_preview(self, obj):
        if obj.qr_code_image:
            return mark_safe(f'<img src="{obj.qr_code_image.url}" width="150" height="150"/>')
        return "No Image"


admin.site.register(Menu, MenuAdmin)
