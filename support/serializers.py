from rest_framework import serializers

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'message',
            # 'post',
            'author',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'author',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        post = Comment.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        return post


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
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

    def create(self, validated_data):
        post = Post.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        return post
