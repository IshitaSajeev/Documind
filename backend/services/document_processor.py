import PyPDF2
import docx


class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path):
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_path):
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX processing failed: {str(e)}")

    @staticmethod
    def extract_text_from_txt(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"TXT processing failed: {str(e)}")

    @classmethod
    def process_document(cls, file_path, file_type):
        if file_type == 'pdf':
            return cls.extract_text_from_pdf(file_path)
        elif file_type == 'docx':
            return cls.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            return cls.extract_text_from_txt(file_path)
        else:
            raise Exception(f"Unsupported file type: {file_type}")
