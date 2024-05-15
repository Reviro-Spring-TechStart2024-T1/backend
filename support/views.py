from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Comment, Post
from .serializers import CommentDetailsSerializer, CommentSerializer, PostSerializer


class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


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


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            return super().update(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to update this comment.')

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            return super().delete(request, *args, **kwargs)
        else:
            raise PermissionDenied('You are not allowed to delete this comment.')
