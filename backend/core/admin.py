from django.contrib import admin
from .models import Document, Question


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'file_type', 'processing_status', 'created_at')
    list_filter = ('file_type', 'processing_status')
    search_fields = ('title', 'user__username')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'document', 'created_at')
    search_fields = ('question_text',)
