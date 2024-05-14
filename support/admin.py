from django.contrib import admin

from .models import Comment, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'content',
        'created_at',
        'updated_at',
        'author',
    )
    search_fields = ('title', 'content', 'author')


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'message',
        'post',
        'author',
        'created_at',
        'updated_at',
    )
    search_fields = ('message', 'author', 'post')


admin.site.register(Comment, CommentAdmin)
