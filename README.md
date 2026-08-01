# DocuMind 📚

> Intelligent Document Summarizer & Q&A System

## 🚀 Features

- 📄 **Multi-format Support**: PDF, DOCX, TXT
- 🤖 **AI Summarization**: Generates concise summaries using BART
- ❓ **Q&A System**: Ask questions about your documents
- 🔐 **JWT Authentication**: Secure API access
- 🐳 **Containerized**: Easy deployment with Docker
- 📊 **API Documentation**: Swagger/OpenAPI

## 🛠️ Tech Stack

**Backend**: Django, Django REST Framework, Celery, Redis
**AI/ML**: Transformers, Sentence Transformers, FAISS
**Database**: PostgreSQL
**DevOps**: Docker, Docker Compose, Gunicorn

## 📦 Installation

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/<your-username>/documind.git
cd documind

# Copy environment variables
cp backend/.env.example backend/.env

# Start services
docker-compose up --build
```

### Manual Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Get JWT token |
| POST | `/api/documents/upload/` | Upload document |
| GET | `/api/documents/` | List documents |
| GET | `/api/documents/{id}/` | Get document details |
| POST | `/api/documents/{id}/ask/` | Ask question |
| GET | `/api/documents/{id}/questions/` | Get question history |

## 🎯 Usage Example

### Upload Document

```python
import requests

# Get token
auth_response = requests.post(
    'http://localhost:8000/api/token/',
    json={'username': 'your-username', 'password': 'your-password'}
)
token = auth_response.json()['access']

# Upload document
headers = {'Authorization': f'Bearer {token}'}
files = {'file': open('document.pdf', 'rb')}
response = requests.post(
    'http://localhost:8000/api/documents/upload/',
    headers=headers,
    files=files
)
print(response.json())
```

### Ask Question

```python
question_data = {'question': 'What is the main topic?'}
response = requests.post(
    f'http://localhost:8000/api/documents/{document_id}/ask/',
    headers=headers,
    json=question_data
)
print(response.json())
```

## 🧪 Testing

```bash
python manage.py test
```

## 📈 Performance (typical)

- Document processing: ~5-10 seconds for a 100-page PDF
- Summarization: ~2-3 seconds
- Q&A response: <1 second

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📄 License

[MIT](LICENSE)
