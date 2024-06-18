from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Comment, Post
from .serializers import CommentDetailsSerializer, CommentSerializer, PostSerializer


class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Create post',
        description=(
            'Allows authenticated user of any role create a post.\n'
            '- Requires authentication.'
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @extend_schema(
        summary='Get posts',
        description=(
            'Allows authenticated user of any role to get a list of posts.\n'
            '- Requires authentication.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PostDetailsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            return super().update(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to update this post.')

    @extend_schema(
        summary='Update post',
        description=(
            'Allows user who created their post to update it.\n'
            '- Requires authentication.\n'
            '- User is able to update post if they are the author of it.'
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Partially update post',
        description=(
            'Allows user who created their post to partially update it.\n'
            '- Requires authentication.\n'
            '- User is able to partially update post if they are the author of it.'
        )
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary='Get post',
        description=(
            'Allows user to get specific post.\n'
            '- Requires authentication.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Delete post',
        description=(
            'Allows user who created their post to delete it.\n'
            '- Requires authentication.\n'
            '- User is able to delete post if they are the author of it.'
        )
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            return super().delete(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to delete this post.')


class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Comment.objects.filter(author=self.request.user)
        return queryset

    @extend_schema(
        summary='Get comments',
        description=(
            'Allows users to get list of all comments.\n'
            '- Requires authentication.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary='Create comment',
        description=(
            'Allows users to create comment.\n'
            '- Requires authentication.'
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Get comment',
        description=(
            'Allows users to get specific comment.\n'
            '- Requires authentication.'
        )
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            return super().update(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to update this comment.')

    @extend_schema(
        summary='Update comment',
        description=(
            'Allows users to update their comment.\n'
            '- Requires authentication.'
        )
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary='Partially update comment',
        description=(
            'Allows users to partially update their comment.\n'
            '- Requires authentication.'
        )
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary='Delete comment',
        description=(
            'Allows users to delete their comment.\n'
            '- Requires authentication.'
        )
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            return super().delete(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to delete this comment.')
