import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from core.models import Document, Question
from .serializers import DocumentSerializer, QuestionSerializer
from services.document_processor import DocumentProcessor
from services.summarizer import DocumentSummarizer
from services.qa_system import QuestionAnsweringSystem
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.parsers import MultiPartParser, FormParser

class DocumentUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='PDF, DOCX, or TXT file to upload'
            )
        ]
    )
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determine file type
        file_name = file.name
        file_type = file_name.split('.')[-1].lower()

        if file_type not in ['pdf', 'docx', 'txt']:
            return Response(
                {'error': f'Unsupported file type: {file_type}. Use PDF, DOCX, or TXT.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save file temporarily
        temp_path = default_storage.save(f'temp_{file_name}', ContentFile(file.read()))
        temp_full_path = default_storage.path(temp_path)

        try:
            # Process document
            content = DocumentProcessor.process_document(temp_full_path, file_type)

            # Create document record
            document = Document.objects.create(
                user=request.user,
                title=file_name,
                file=temp_path,
                file_type=file_type,
                content=content,
                processed=False,
                processing_status='pending'
            )

            # Start async summarization (in production, use Celery)
            # For now, sync processing
            self.process_document_sync(document, content)

            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_full_path):
                os.remove(temp_full_path)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def process_document_sync(self, document, content):
        try:
            document.processing_status = 'processing'
            document.save()

            # Summarize
            summarizer = DocumentSummarizer()
            summary = summarizer.summarize(content)
            document.summary = summary

            # Initialize QA system
            qa_system = QuestionAnsweringSystem()
            qa_system.initialize_embeddings(content)

            # Save QA index
            index_path = f'qa_indices/{document.id}'
            qa_system.save_index(index_path)

            document.processed = True
            document.processing_status = 'completed'
            document.save()

        except Exception as e:
            document.processing_status = 'failed'
            document.save()
            raise e


class DocumentListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.filter(user=request.user)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)


class DocumentDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, user=request.user)
        serializer = DocumentSerializer(document)
        return Response(serializer.data)

    def delete(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, user=request.user)
        document.delete()
        return Response(
            {'message': 'Document deleted successfully'},
            status=status.HTTP_200_OK
        )


class AskQuestionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['question'],
            properties={
                'question': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Question to ask about the document'
                ),
            },
        )
    )

    def post(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, user=request.user)

        if not document.processed:
            return Response(
                {'error': 'Document is still processing'},
                status=status.HTTP_400_BAD_REQUEST
            )

        question_text = request.data.get('question')
        if not question_text:
            return Response(
                {'error': 'Question is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Load QA system
            qa_system = QuestionAnsweringSystem()
            index_path = f'qa_indices/{document.id}'

            if not os.path.exists(index_path + '.faiss'):
                # Re-initialize if index missing
                qa_system.initialize_embeddings(document.content)
                qa_system.save_index(index_path)
            else:
                qa_system.load_index(index_path)

            # Get answer
            answer = qa_system.ask_question(question_text)

            # Save question
            question = Question.objects.create(
                document=document,
                question_text=question_text,
                answer=answer
            )

            return Response({
                'question': question_text,
                'answer': answer,
                'id': question.id
            })

        except Exception as e:
            return Response(
                {'error': f'Failed to answer question: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionHistoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        document = get_object_or_404(Document, id=document_id, user=request.user)
        questions = Question.objects.filter(document=document)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
