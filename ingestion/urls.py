from django.urls import path
from .views import DataIngestionView, ReviewQueueView, ApproveRecordView

urlpatterns = [
    path('upload/', DataIngestionView.as_view(), name='data-upload'),
    path('review/', ReviewQueueView.as_view(), name='review-queue'),
    path('approve/<int:pk>/', ApproveRecordView.as_view(), name='approve-record'),
]