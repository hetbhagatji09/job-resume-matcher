import re
import string
import unicodedata
from nltk.corpus import stopwords

class TextCleaningService:

    def __init__(self):
        try:
            self.stop_words = set(stopwords.words("english"))
        except:
            import nltk
            nltk.download("stopwords")
            self.stop_words = set(stopwords.words("english"))

    def clean(self, text: str) -> str:
        """ Clean text for embedding — removes noise, stopwords, punctuation """

        if not text:
            return ""

        # Normalize accented chars
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

        # Lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r"http\S+|www\S+", " ", text)

        # Remove numbers
        text = re.sub(r"\d+", " ", text)

        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))

        # Tokenize
        tokens = text.split()

        # Remove stopwords
        tokens = [t for t in tokens if t not in self.stop_words]

        # Remove short meaningless words
        tokens = [t for t in tokens if len(t) > 2]

        # Join back
        cleaned = " ".join(tokens)

        # Collapse extra spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned
