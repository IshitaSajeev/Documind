from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch


class DocumentSummarizer:
    def __init__(self):
        # Using a smaller, efficient model
        model_name = "facebook/bart-large-cnn"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
            self.summarizer = pipeline(
                "summarization",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
        except Exception as e:
            print(f"Model load failed: {e}. Using fallback.")
            self.summarizer = None

    def summarize(self, text, max_length=150, min_length=30):
        """
        Generate summary of input text
        """
        if not text or len(text) < 100:
            return text or "Text is too short for summarization."

        if self.summarizer is None:
            # Fallback: return first few sentences
            sentences = text.split('.')
            summary = '.'.join(sentences[:3]) + '.'
            return summary

        # Truncate if too long (model has context window limits)
        max_input_length = 1024
        if len(text) > max_input_length * 4:
            text = text[:max_input_length * 4]

        try:
            result = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            return result[0]['summary_text']
        except Exception as e:
            print(f"Summarization failed: {e}")
            # Fallback
            sentences = text.split('.')
            return '.'.join(sentences[:5]) + '.'

    def extract_key_phrases(self, text, top_n=5):
        """
        Extract key phrases from document using simple frequency-based approach
        """
        from collections import Counter
        import re

        # Tokenize and clean
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        word_freq = Counter(words)
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out'}

        # Get most common words excluding stopwords
        common = [(word, count) for word, count in word_freq.items()
                  if word not in stopwords and len(word) > 3]
        common.sort(key=lambda x: x[1], reverse=True)

        return [word for word, count in common[:top_n]]
