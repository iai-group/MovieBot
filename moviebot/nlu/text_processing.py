"""This module is used for preprocessing user inputs before further analysis.
The user utterance is broken into tokens which contain additional information
about the it.
"""

from typing import Text, List, Optional

import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


class Token:
    """Subpart of an utterance. Contains mapping of start and end positions in
    the original utterance. In addition it stores the lemmatized version of
    the token and whether it is a stopword or not.
    """

    def __init__(self,
                 text: Text,
                 start: int,
                 end: Optional[int] = None,
                 lemma: Optional[Text] = None,
                 is_stopword: Optional[bool] = False) -> None:
        self.text = text

        self.start = start
        self.end = end if end else len(text)

        self.lemma = lemma if lemma else text
        self.is_stopword = is_stopword

    def overlaps(self, other) -> bool:
        """Checks whether two tokens overlap in the original utterance.

        Args:
            other (Token): Token to compare against

        Returns:
            bool: True if there is overlap.
        """
        return (self.start < other.start
                and self.end >= other.start) or (other.start < self.start
                                                 and other.end >= self.start)

    def __lt__(self, other):
        return (self.start, self.end) < (other.start, other.end)

    def __add__(self, other):
        sorted_tokens = sorted((self, other))
        text = ' '.join(token.text for token in sorted_tokens)
        lemma = ' '.join(token.lemma for token in sorted_tokens)

        return Token(text, sorted_tokens[0].start, sorted_tokens[1].end, lemma)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)


class TextProcess:
    """This class contains methods needed for preprocessing sentences.
    """

    def __init__(self, additional_stop_words: List[Text] = None) -> None:
        stop_words = stopwords.words('english')
        if additional_stop_words:
            stop_words.extend(additional_stop_words)

        self._stop_words = set(stop_words)
        self._lemmatizer = WordNetLemmatizer()
        self._punctuation = set(string.punctuation.replace('\'', ''))

    def process_text(self, text: Text) -> List[Token]:
        """Processes given text. The text is split into tokens which can be
        mapped back to the original text.

        Args:
            text (Text): Input text, user utterance.

        Returns:
            List[Token]: List of Tokens
        """
        processed_text = self.remove_punctuation(text)
        word_tokens = processed_text.split()  #word_tokenize(processed_text)

        return self.tokenize(word_tokens, text)

    def remove_punctuation(self, text: Text) -> Text:
        """Defines patterns of punctuation marks to remove in the
        utterance.

        Args:
            text (str): Sentence.

        Returns:
            str: Sentence without punctuation.
        """
        return ''.join(
            ch if ch not in self._punctuation else ' ' for ch in text)

    def lemmatize_text(self, text: Text) -> Text:
        """Returns string lemma.

        Args:
            text (Text): Input text.

        Returns:
            Text: Lemmatized string.
        """
        text = text.replace('\'', '')
        return self._lemmatizer.lemmatize(text.lower())

    def tokenize(self, word_tokens: List[Text], text: Text) -> List[Token]:
        """Returns a tokenized copy of text.

        Args:
            text (str): Sentence to tokenize.

        Returns:
            List[str]: List of tokens.
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
