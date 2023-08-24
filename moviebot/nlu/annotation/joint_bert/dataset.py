import re

import torch
import yaml
from torch.utils.data import Dataset
from transformers import BertTokenizer

from moviebot.nlu.annotation.joint_bert.slot_mapping import (
    JointBERTIntent,
    JointBERTSlot,
)

_IGNORE_INDEX = -100

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def parse_data(data):
    """Parses the input data to extract intent, text, and slot annotations."""
    for intent in data.keys():
        for annotated_example in data[intent]:
            # Extract slot information
            slot_annotations = re.findall(
                r"\[(.*?)\]\((.*?)\)", annotated_example
            )

            # Remove slot annotations from the text
            clean_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", annotated_example)

            yield intent, clean_text, slot_annotations


def tokenize_and_label(intent, text, slot_annotations):
    """Tokenizes the text and assigns labels based on slot annotations."""
    tokens = tokenizer.tokenize(text)
    labels = []

    start_idx = 0
    for slot_text, slot_label in slot_annotations:
        index = text.find(slot_text)
        for word in text[start_idx:index].split():
            labels.append(JointBERTSlot.to_index("OUT"))
            labels.extend([_IGNORE_INDEX] * len(tokenizer.tokenize(word)[1:]))

        for i, word in enumerate(slot_text.split()):
            labels.append(
                JointBERTSlot.to_index(
                    ("B_" if i == 0 else "I_") + slot_label.upper()
                )
            )
            labels.extend([_IGNORE_INDEX] * len(tokenizer.tokenize(word)[1:]))
        start_idx = index + len(slot_text)

    for word in text[start_idx:].split():
        labels.append(JointBERTSlot.to_index("OUT"))
        labels.extend([_IGNORE_INDEX] * len(tokenizer.tokenize(word)[1:]))
    assert len(tokens) == len(labels)
    return JointBERTIntent.to_index(intent.upper()), tokens, labels


# def tokenize_and_label(intent, text, slot_annotations):
#     """Tokenizes the text and assigns labels based on slot annotations."""
#     tokens = tokenizer.tokenize(text)
#     labels = [JointBERTSlot.to_index("OUT")] * len(
#         tokens
#     )  # Initialize all labels as 'OUT'

#     for slot_text, slot_label in slot_annotations:
#         if slot_label == "modifier":
#             print(slot_text)
#             continue
#         slot_tokens = tokenizer.tokenize(slot_text)

#         # Find the start position of slot tokens
#         start_pos = None
#         for i in range(len(tokens) - len(slot_tokens) + 1):
#             if tokens[i : i + len(slot_tokens)] == slot_tokens:
#                 start_pos = i
#                 break

#         # Assign B- and I- labels based on the slot label
#         if start_pos is not None:
#             labels[start_pos] = JointBERTSlot.to_index(
#                 f"B_{slot_label.upper()}"
#             )
#             for i in range(1, len(slot_tokens)):
#                 labels[start_pos + i] = JointBERTSlot.to_index(
#                     f"I_{slot_label.upper()}"
#                 )

#     return JointBERTIntent.to_index(intent.upper()), tokens, labels


class JointBERTDataset(Dataset):
    def __init__(self, path):
        self.data = load_yaml(path)
        self.examples = []
        self._build_dataset()

    def _build_dataset(self):
        for intent, clean_text, slot_annotations in parse_data(self.data):
            intent, tokens, labels = tokenize_and_label(
                intent, clean_text, slot_annotations
            )

            input_ids = tokenizer.encode(tokens, add_special_tokens=True)

            # Add special tokens to label list
            cls_label = _IGNORE_INDEX
            sep_label = _IGNORE_INDEX
            labels = [cls_label] + labels + [sep_label]

            attention_mask = [1] * len(input_ids)

            # Pad sequences to a fixed length (e.g., 128)
            # This value can be adjusted based on the average/max sequence length in your dataset.
            max_length = 32
            padding_length = max_length - len(input_ids)

            input_ids = input_ids + ([0] * padding_length)
            attention_mask = attention_mask + ([0] * padding_length)
            labels = labels + ([_IGNORE_INDEX] * padding_length)
            self.examples.append((input_ids, attention_mask, intent, labels))

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        input_ids, attention_mask, intent, labels = self.examples[idx]

        return (
            torch.tensor(input_ids, dtype=torch.long),
            torch.tensor(attention_mask, dtype=torch.long),
            torch.tensor(intent, dtype=torch.long),
            torch.tensor(labels, dtype=torch.long),
        )


if __name__ == "__main__":
    # Sample input data
    path = "data/training/utterances_chatGPT_clean.yaml"
    # dataset = JointBERTDataset(path)
    # print(dataset[0])
    # print(tokenizer.decode(dataset[0][3]))
    data = load_yaml(path)
    i = 0
    for intent, clean_text, slot_annotations in parse_data(data):
        print(intent, clean_text, slot_annotations)
        intent, tokens, labels = tokenize_and_label(
            intent, clean_text, slot_annotations
        )
        print(intent, tokens, labels)
        i += 1
        if i == 10:
            break
