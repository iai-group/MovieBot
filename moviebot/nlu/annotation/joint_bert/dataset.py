"""Dataset loading for training and evaluating the JointBERT model. """
import os
import re
from typing import Dict, Generator, List, Tuple

import torch
import yaml
from torch.utils.data import Dataset
from transformers import BertTokenizer

from moviebot.nlu.annotation.joint_bert.slot_mapping import (
    JointBERTIntent,
    JointBERTSlot,
)

DataPoint = Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]

_IGNORE_INDEX = -100
_TOKENIZER_PATH = "bert-base-uncased"


def load_yaml(path: str) -> Dict[str, List[str]]:
    """Loads the YAML file at the given path.

    Args:
        path: The path to the YAML file.

    Raises:
        FileNotFoundError: If the file does not exist.

    Returns:
        The data in the YAML file.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(path) as f:
        return yaml.safe_load(f)


def parse_data(
    data: Dict[str, List[str]]
) -> Generator[Tuple[str, str, List[str]], None, None]:
    """Parses the input data to extract intent, text, and slot annotations.

    Args:
        data: The input data.

    Yields:
        A tuple of the intent, text, and slot annotations.
    """
    for intent in data.keys():
        for annotated_example in data[intent]:
            # Extract slot information
            slot_annotations = re.findall(
                r"\[(.*?)\]\((.*?)\)", annotated_example
            )

            # Remove slot annotations from the text
            clean_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", annotated_example)

            yield intent, clean_text, slot_annotations


class JointBERTDataset(Dataset):
    def __init__(self, path: str, max_length: int = 32) -> None:
        """Initializes the dataset.

        Args:
            path: The path to the YAML file containing the data.
            max_length: The maximum length of the input sequence. Defaults to
                32.
        """
        self.data = load_yaml(path)
        self.max_length = max_length

        self.intent_label_count = len(JointBERTIntent)
        self.slot_label_count = len(JointBERTSlot)

        self.tokenizer = BertTokenizer.from_pretrained(_TOKENIZER_PATH)

        self.examples = []
        self._build_dataset()

    def _build_dataset(self) -> None:
        """Builds the dataset."""
        for intent, clean_text, slot_annotations in parse_data(self.data):
            intent, tokens, labels = self._tokenize_and_label(
                intent, clean_text, slot_annotations
            )

            input_ids = self.tokenizer.encode(tokens, add_special_tokens=True)
            attention_mask = [1] * len(input_ids)

            # Add [CLS] and [SEP] tokens to labels
            cls_label = _IGNORE_INDEX
            sep_label = _IGNORE_INDEX
            labels = [cls_label] + labels + [sep_label]

            # Pad input_ids, attention_mask, and labels
            padding_length = self.max_length - len(input_ids)
            input_ids = input_ids + (
                [self.tokenizer.pad_token_id] * padding_length
            )
            attention_mask = attention_mask + ([0] * padding_length)
            labels = labels + ([_IGNORE_INDEX] * padding_length)
            self.examples.append((input_ids, attention_mask, intent, labels))

    def _num_inside_word_tokens(self, word: str) -> int:
        """Returns the number of inside word tokens in the input word.

        I.e The number of non-starting tokens in the word.

        Args:
            word: The input word.

        Returns:
            The number of word tokens in the input word.
        """
        return len(self.tokenizer.tokenize(word)) - 1

    def _tokenize_and_label(
        self, intent: str, text: str, slot_annotations: Tuple[str, str]
    ) -> Tuple[int, List[str], List[int]]:
        """Tokenizes the text and assigns labels based on slot annotations.

        The main purpose of this method is to convert the slot annotations into
        labels that can be used to train the model. The labels need to have the
        same length as the tokenized utterance.

        For example:

        Input: "I like scifi."
        Tokens: ["I", "like", "sci", "##fi", "."]
        Labels: ["OUT", "OUT", "B_GENRE", -100, "OUT"]
        Indexes: [0, 0, 3, -100, 0]

        Note that we put -100 to ignore evaluation of the loss function for
        tokens that are not beginning of a slot. This makes it easier to
        decode the labels later.

        Args:
            intent: The intent of the text.
            text: The text to tokenize.
            slot_annotations: A tuple of slot-value pairs in the text.

        Returns:
            A tuple of the intent, tokenized text, and labels.
        """
        tokens = self.tokenizer.tokenize(text)
        labels = []

        start_idx = 0
        for slot_text, slot_label in slot_annotations:
            index = text.find(slot_text)
            for word in text[start_idx:index].split():
                labels.append(JointBERTSlot.to_index("OUT"))
                labels.extend(
                    [_IGNORE_INDEX] * self._num_inside_word_tokens(word)
                )

            for i, word in enumerate(slot_text.split()):
                slot = (
                    ("B" if i == 0 else "I")
                    + ("_INQUIRE_" if intent == "INQUIRE" else "_PREFERENCE_")
                    + slot_label.upper()
                )

                labels.append(JointBERTSlot.to_index(slot))
                labels.extend(
                    [_IGNORE_INDEX] * self._num_inside_word_tokens(word)
                )
            start_idx = index + len(slot_text)

        for word in text[start_idx:].split():
            labels.append(JointBERTSlot.to_index("OUT"))
            labels.extend([_IGNORE_INDEX] * self._num_inside_word_tokens(word))
        assert len(tokens) == len(labels)
        return JointBERTIntent.to_index(intent.upper()), tokens, labels

    def __len__(self):
        """Returns the number of examples in the dataset."""
        return len(self.examples)

    def __getitem__(self, idx: int) -> DataPoint:
        """Returns the example at the given index.

        Args:
            idx: The index of the example to return.

        Returns:
            A tuple of the input_ids, attention_mask, intent, and labels.
        """
        input_ids, attention_mask, intent, labels = self.examples[idx]

        return (
            torch.tensor(input_ids, dtype=torch.long),
            torch.tensor(attention_mask, dtype=torch.long),
            torch.tensor(intent, dtype=torch.long),
            torch.tensor(labels, dtype=torch.long),
        )
