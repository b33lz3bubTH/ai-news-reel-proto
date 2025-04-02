import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data (one-time)
nltk.download('punkt')
nltk.download('stopwords')

class Summarizer:
    def __init__(self, num_sentences=3):
        """Initialize with desired number of sentences in summary."""
        self.num_sentences = num_sentences
        self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text):
        """Clean the text by removing URLs, emojis, quotes, and other noise."""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Remove pic.twitter.com links
        text = re.sub(r'pic\.twitter\.com/[a-zA-Z0-9]+', '', text)
        # Remove quotes (single and double)
        text = re.sub(r'["\']', '', text)
        # Remove emojis
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def generate(self, text):
        """Generate a summary of the input text."""
        # Clean the text first
        cleaned_text = self.clean_text(text)

        # Tokenize words and sentences from cleaned text
        words = word_tokenize(cleaned_text.lower())
        sentences = sent_tokenize(cleaned_text)

        # Calculate word frequencies
        word_freq = {}
        for word in words:
            if word not in self.stop_words and word.isalnum():
                word_freq[word] = word_freq.get(word, 0) + 1

        # Score sentences based on word frequencies
        sentence_scores = {}
        for sent in sentences:
            for word, freq in word_freq.items():
                if word in sent.lower():
                    sentence_scores[sent] = sentence_scores.get(sent, 0) + freq

        # Select top sentences for summary
        summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:self.num_sentences]
        return ' '.join(summary_sentences)
