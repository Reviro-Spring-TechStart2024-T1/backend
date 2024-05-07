from django.contrib import admin

from .models import Beverage, Category, Menu


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)


class BeverageAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'in_stock', 'menu')
    list_filter = ('category', 'menu', 'in_stock')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {'fields': ('menu', 'name', 'category', 'price', 'in_stock')}),
        ('Description and Timing', {'fields': ('description',)}),
    )


admin.site.register(Beverage, BeverageAdmin)


class MenuAdmin(admin.ModelAdmin):
    list_display = ('establishment', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('establishment',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


admin.site.register(Menu, MenuAdmin)
