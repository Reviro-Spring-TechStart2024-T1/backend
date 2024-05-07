from rest_framework import generics, permissions

from .models import Feedback
from .seializers import FeedbackSerializer


class FeedbackListView(generics.ListCreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Allow only feedback owner or staff to view and modify feedback"""
        if self.request.user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.filter(user=self.request.user)
