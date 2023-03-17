"""This module is used for preprocessing user inputs before further analysis.

The user utterance is broken into tokens which contain additional
information about the it.
"""

import string
from typing import List, Optional

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class Span:
    def __init__(
        self,
        text: str,
        start: int,
        end: Optional[int] = None,
        lemma: Optional[str] = None,
    ) -> None:
        """Subpart of an utterance.

        Contains mapping of start and end positions in the original
        utterance.

        Args:
            text: Raw token string.
            start: Start of the token in utterance.
            end: End of token in utterance. Defaults to None.
            lemma: Lemmatized token string. Defaults to None.
        """
        self.text = text

        self.start = start
        self.end = end if end else start + len(text)

        self.lemma = lemma if lemma else text

    def overlaps(self, other: "Span") -> bool:
        """Checks whether two spans overlap in the original utterance.

        Args:
            other: Span to compare against.

        Returns:
            True if there is overlap.
        """
        return (self.start <= other.start and self.end > other.start) or (
            other.start <= self.start and other.end > self.start
        )

    def __eq__(self, other: "Span") -> bool:
        s_dict = vars(self)
        o_dict = vars(other)
        return type(self) is type(other) and all(
            (s_dict.get(k) == v for k, v in o_dict.items())
        )

    def __lt__(self, other: "Span") -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __add__(self, other: "Span") -> "Span":
        sorted_spans = sorted((self, other))
        text = " ".join(span.text for span in sorted_spans)
        lemma = " ".join(span.lemma for span in sorted_spans)

        return Span(text, sorted_spans[0].start, sorted_spans[1].end, lemma)

    def __radd__(self, other: "Span") -> "Span":
        if other == 0:
            return self
        else:
            return self.__add__(other)


class Token(Span):
    def __init__(
        self,
        text: str,
        start: int,
        end: Optional[int] = None,
        lemma: Optional[str] = None,
        is_stop: Optional[bool] = False,
    ) -> None:
        """Token is a smaller unit than Span.

        While Span can stretch over several words, Token contains only
        single words. Token stores additional information about the word.

        Args:
            text: Raw token string.
            start: Start of the token in utterance.
            end: End of token in utterance. Defaults to None.
            lemma: Lemmatized token string. Defaults to None.
            is_stop: If true, the token is a stop word. Defaults to False.
        """
        super().__init__(text, start, end, lemma)
        self.is_stop = is_stop


class Tokenizer:
    def __init__(self, additional_stop_words: List[str] = None) -> None:
        """This class contains methods needed for preprocessing sentences.

        Args:
            additional_stop_words: Stop words to use in addition to NLTK
              stopword list.
        """
        stop_words = stopwords.words("english")
        if additional_stop_words:
            stop_words.extend(additional_stop_words)

        self._stop_words = set(stop_words)
        self._lemmatizer = WordNetLemmatizer()
        self._punctuation = set(string.punctuation.replace("'", ""))

    def process_text(self, text: str) -> List[Token]:
        """Processes given text.

        The text is split into tokens which can be mapped back to the original
        text.

        Args:
            text: A piece of text.

        Returns:
            List of tokens.
        """
        processed_text = self.remove_punctuation(text)
        word_tokens = processed_text.split()

        return self.tokenize(word_tokens, text)

    def remove_punctuation(self, text: str) -> str:
        """Defines patterns of punctuation marks to remove in the utterance.

        Args:
            text: A piece of text.

        Returns:
            A piece of text without punctuation.
        """
        return "".join(
            ch if ch not in self._punctuation else " " for ch in text
        )

    def lemmatize_text(self, text: str) -> str:
        """Returns string lemma.

        Args:
            text: A piece of text.

        Returns:
            Lemmatized piece of text.
        """
        text = text.replace("'", "")
        return self._lemmatizer.lemmatize(text.lower())

    def tokenize(self, word_tokens: List[str], text: str) -> List[Token]:
        """Returns a tokenized copy of text.

        Args:
            text: A piece of text.

        Returns:
            List of tokens.
        """
        end = 0
        tokens = []
        for word in word_tokens:
            start = text.index(word, end)
            end = start + len(word)
            lemma = self.lemmatize_text(word)
            is_stopword = word in self._stop_words

            tokens.append(Token(word, start, end, lemma, is_stopword))
        return tokens
