from django.contrib import admin
from .models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'establishment', 'rating', 'comment_preview')
    list_filter = ('rating', 'establishment')
    search_fields = ('user__name', 'establishment__name', 'comment')
    readonly_fields = ('user', 'establishment')

    def comment_preview(self, obj):
        return obj.comment[:40] + '...' if len(obj.comment) > 40 else obj.comment

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only include feedback from customers; might need adjustments depending on the exact requirement
        return qs.filter(user__role='customer')


admin.site.register(Feedback, FeedbackAdmin)
