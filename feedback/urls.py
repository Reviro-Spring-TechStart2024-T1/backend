from django.urls import path
from .views import FeedbackListView, FeedbackDetailView

urlpatterns = [
    path('', FeedbackListView.as_view(), name='feedback-list'),
    path('<int:pk>/', FeedbackDetailView.as_view(), name='feedback-detail'),
]
