from django.urls import path
from .views import (
    DocumentUploadView,
    DocumentListView,
    DocumentDetailView,
    AskQuestionView,
    QuestionHistoryView
)

urlpatterns = [
    path('documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/<uuid:document_id>/', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<uuid:document_id>/ask/', AskQuestionView.as_view(), name='ask-question'),
    path('documents/<uuid:document_id>/questions/', QuestionHistoryView.as_view(), name='question-history'),
]
