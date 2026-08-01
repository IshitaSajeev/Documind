from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os


class QuestionAnsweringSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        self.dimension = 384  # all-MiniLM-L6-v2 embedding size

    def initialize_embeddings(self, document_text, chunk_size=200):
        """
        Create FAISS index from document chunks
        """
        # Split text into chunks
        words = document_text.split()
        self.chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

        if not self.chunks:
            return False

        # Generate embeddings
        embeddings = self.model.encode(self.chunks)

        # Normalize and create FAISS index
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype('float32'))

        return True

    def ask_question(self, question, top_k=3):
        """
        Find most relevant answer from document context
        """
        if self.index is None or not self.chunks:
            return "Document has not been processed for Q&A. Please initialize embeddings first."

        # Encode question
        question_embedding = self.model.encode([question])
        question_embedding = question_embedding / np.linalg.norm(question_embedding, axis=1, keepdims=True)

        # Search
        distances, indices = self.index.search(question_embedding.astype('float32'), top_k)

        # Get most relevant chunks
        relevant_chunks = [self.chunks[i] for i in indices[0] if i < len(self.chunks)]

        if not relevant_chunks:
            return "No relevant information found in the document."

        # Simple answer extraction: find sentence with best context
        best_chunk = relevant_chunks[0]
        sentences = best_chunk.split('.')
        if len(sentences) > 1:
            # Find sentence closest to question
            sentence_embeddings = self.model.encode(sentences)
            question_emb = self.model.encode([question])[0]

            # Calculate similarities
            similarities = np.dot(sentence_embeddings, question_emb)
            best_idx = np.argmax(similarities)

            return sentences[best_idx].strip() + '.'

        # If no good sentences found, return full chunk
        return best_chunk[:500] + '...'

    def save_index(self, filepath):
        """
        Save FAISS index and chunks to disk
        """
        if self.index is None:
            return False

        # Ensure the target directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Save chunks
        chunks_path = filepath + '_chunks.pkl'
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)

        # Save FAISS index
        faiss.write_index(self.index, filepath + '.faiss')

        return True

    def load_index(self, filepath):
        """
        Load FAISS index and chunks from disk
        """
        try:
            chunks_path = filepath + '_chunks.pkl'
            with open(chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)

            self.index = faiss.read_index(filepath + '.faiss')
            return True
        except Exception as e:
            print(f"Failed to load index: {e}")
            return False
