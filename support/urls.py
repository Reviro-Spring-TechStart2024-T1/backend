from django.urls import path

from .views import CommentDetailView, CommentListView, PostDetailsView, PostListView

urlpatterns = [
    path('posts/', PostListView.as_view(), name='posts'),
    path('posts/<int:pk>/', PostDetailsView.as_view(), name='post_details'),
    path('comments/', CommentListView.as_view(), name='comments'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment_details')
]
