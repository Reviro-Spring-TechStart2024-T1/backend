from rest_framework import serializers

from accounts.models import User

from .models import Comment, Post


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'avatar'
        ]


class CommentDetailsSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'message',
            'post',
            'author',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'post',
            'author',
            'created_at',
            'updated_at',
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
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

    def create(self, validated_data):
        post = Comment.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        return post


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        comments = instance.comments.filter(is_deleted=False)
        comments_serializer = CommentSerializer(comments, many=True, context=self.context)
        representation['comments'] = comments_serializer.data

        return representation
