import os

import torch
from torch.utils.data import Dataset
from transformers import BertTokenizer

_SNIPS_DATA_PATH = "/Users/2920807/Repos/Slot_Filling/dataset/snips"
_IGNORE_INDEX = -100

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


def clean_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.read().splitlines()]


def load_data(
    mode="train",
):
    folder_path = os.path.join(_SNIPS_DATA_PATH, mode)
    intents_data = clean_text(os.path.join(folder_path, "label"))

    all_intents_path = os.path.join(_SNIPS_DATA_PATH, "all_intents")
    if os.path.isfile(all_intents_path):
        intents = clean_text(all_intents_path)
    else:
        intents = list(set(intents_data))
        with open(all_intents_path, "w") as f:
            f.write("\n".join(intents))

    utterances_data = clean_text(os.path.join(folder_path, "seq.in"))
    labels_data = clean_text(os.path.join(folder_path, "seq.out"))

    all_labels_path = os.path.join(_SNIPS_DATA_PATH, "all_labels")
    if os.path.isfile(all_labels_path):
        labels = clean_text(all_labels_path)
    else:
        labels = list(
            set(label.strip() for row in labels_data for label in row.split())
        )
        with open(all_labels_path, "w") as f:
            f.write("\n".join(labels))

    return (intents, labels), (intents_data, utterances_data, labels_data)


class JointBERTDataset(Dataset):
    def __init__(self, mode="train"):
        self.data = load_data(mode)
        self.examples = []
        self._build_dataset()

    def _build_dataset(self):
        (all_intents, all_labels), (
            intents_data,
            utterances_data,
            labels_data,
        ) = self.data

        self.intent_label_count = len(all_intents)
        self.slot_label_count = len(all_labels)

        for intent, utterance, labels in zip(
            intents_data, utterances_data, labels_data
        ):
            assert len(utterance.split()) == len(labels.split())
            tokens = []
            slot_labels = []
            for word, label in zip(utterance.split(), labels.split()):
                word_tokens = tokenizer.tokenize(word)
                tokens.extend(
                    word_tokens if word_tokens else [tokenizer.unk_token]
                )
                slot_labels.append(all_labels.index(label))
                if len(word_tokens) > 1:
                    slot_labels.extend([_IGNORE_INDEX] * len(word_tokens[1:]))

            assert len(tokens) == len(slot_labels)
            input_ids = tokenizer.encode(tokens, add_special_tokens=True)

            # Add special tokens to label list
            cls_label = _IGNORE_INDEX
            sep_label = _IGNORE_INDEX
            labels = [cls_label] + slot_labels + [sep_label]

            attention_mask = [1] * len(input_ids)

            # # Pad sequences to a fixed length (e.g., 128)
            # # This value can be adjusted based on the average/max sequence length in your dataset.
            max_length = 50
            padding_length = max_length - len(input_ids)

            input_ids = input_ids + ([tokenizer.pad_token_id] * padding_length)
            attention_mask = attention_mask + ([0] * padding_length)
            labels = labels + ([_IGNORE_INDEX] * padding_length)
            self.examples.append(
                (input_ids, attention_mask, all_intents.index(intent), labels)
            )

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
    dataset = JointBERTDataset("")
    print(dataset[0])
    # print(tokenizer.decode(dataset[0][3]))
