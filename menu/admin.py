from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import ItemCategory, Menu, MenuItem, QrCode


class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(ItemCategory, ItemCategoryAdmin)


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_category', 'price', 'in_stock', 'menu')
    list_filter = ('item_category', 'menu', 'in_stock')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {'fields': ('menu', 'name', 'item_category', 'price', 'in_stock')}),
        ('Description and Timing', {'fields': ('description',)}),
    )


admin.site.register(MenuItem, MenuItemAdmin)


class MenuAdmin(admin.ModelAdmin):
    list_display = ('establishment', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('establishment',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


admin.site.register(Menu, MenuAdmin)


class QrCodeAdmin(admin.ModelAdmin):
    list_display = ('menu', 'created_at', 'updated_at', 'qr_code_image_preview')
    readonly_fields = ('created_at', 'updated_at', 'qr_code_image_preview')
    fieldsets = (
        (None, {'fields': ('menu', 'qr_code_image', 'qr_code_image_preview')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def qr_code_image_preview(self, obj):
        if obj.qr_code_image:
            return mark_safe(f'<img src="{obj.qr_code_image.url}" width="150" height="150"/>')
        return 'No Image'


admin.site.register(QrCode, QrCodeAdmin)
