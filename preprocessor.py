from collections import Counter

import nltk
from konlpy.tag import Komoran

nltk.download("punkt")


class BasePreprocessor:
    def get_count(text: str, k: int = 100):
        count = Counter(text)
        return count.most_common(k)


class KoreanPreprocessor(BasePreprocessor):
    def __init__(self):
        self.komoran = Komoran()

    def extract_keyword(self, text: str):
        return " ".join([nouns for nouns in self.komoran.nouns(text) if len(nouns) > 1])
