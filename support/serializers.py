from rest_framework import serializers

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'message',
            'post',
            'author',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'author',
            'created_at',
            'updated_at',
        ]


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'created_at',
            'updated_at',
            'author',
            'comments'
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'author',
        ]
