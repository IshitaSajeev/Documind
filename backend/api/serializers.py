from rest_framework import serializers
from core.models import Document, Question


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file_type', 'content', 'summary',
                  'created_at', 'updated_at', 'processed', 'processing_status']
        read_only_fields = ['id', 'created_at', 'updated_at', 'processed',
                             'processing_status', 'content', 'summary']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'answer', 'confidence_score', 'created_at']
        read_only_fields = ['id', 'answer', 'confidence_score', 'created_at']
