"""This module is used for preprocessing user inputs before further analysis.
"""

import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from typing import List


class TextProcess:
    """This class contains methods needed for preprocessing sentences.
    """

    def process_text(self, text: str) -> List[str]:
        processed_text = self.remove_punctuation(text)
        processed_text = self.to_lower(processed_text)
        processed_text = self.tokenize(processed_text)
        processed_text = self.lemmatize_tokens(processed_text)
        processed_text = self.remove_stopwords(processed_text)

        return processed_text

    def to_lower(self, text: str) -> str:
        """Returns sentence without capital letters.

        Args:
            text (str): Sentence.

        Returns:
            str: Same sentence without capital letters.
        """
        return text.lower()

    def remove_punctuation(self, text: str) -> str:
        """Defines patterns of punctuation marks to remove in the
        utterance.

        Args:
            text (str): Sentence.

        Returns:
            str: Sentence without punctuation.
        """
        return ''.join(
            ch if ch not in string.punctuation else ' ' for ch in text)

    def tokenize(self, text: str) -> List[str]:
        """Returns a tokenized copy of text.

        Args:
            text (str): Sentence to tokenize.

        Returns:
            List[str]: List of tokens.
        """
        return word_tokenize(text)

    def lemmatize_tokens(self, word_tokens: List[str]) -> List[str]:
        """Returns lemmatized (inflected) forms of words.

        Args:
            word_tokens (List[str]): list of tokens.

        Returns:
            List[str]: list of lemmatized tokens.
        """

        return [WordNetLemmatizer().lemmatize(word) for word in word_tokens]

    def remove_stopwords(self,
                         word_tokens: List[str],
                         additional_stop_words: List[str] = None) -> List[str]:
        """Removes stopwords from a list of words. Stopwords are the most common
        used words contained in english corpus in nltk package. Additionally,
        it is possible to add a custom list of words to remove from the text.

        Args:
            word_tokens (List[str]): List of tokens
            additional_stop_words (List[str], optional): Custom words to remove
                from the list of tokens. Defaults to None.

        Returns:
            List[str]: List of tokens without stopwords.
        """

        stop_words = stopwords.words('english')
        if additional_stop_words:
            stop_words.extend(additional_stop_words)

        stop_words = set(stop_words)
        return [word for word in word_tokens if word not in stop_words]
