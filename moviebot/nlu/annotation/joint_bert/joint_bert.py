"""Joint BERT model for intent classification and slot annotation."""
from __future__ import annotations

import os
from typing import List, Optional, Tuple

import torch
import torch.nn as nn
from transformers import BertModel

_BERT_BASE_MODEL = "bert-base-uncased"


class JointBERT(nn.Module):
    def __init__(
        self,
        intent_label_count: int,
        slot_label_count: int,
    ) -> None:
        """Initializes the JointBERT model.

        Args:
            intent_label_count: The number of intent labels.
            slot_label_count: The number of slot labels.
        """
        super(JointBERT, self).__init__()

        self.slot_label_count = slot_label_count
        self.intent_label_count = intent_label_count

        self.bert = BertModel.from_pretrained(_BERT_BASE_MODEL)
        self.intent_classifier = nn.Linear(
            self.bert.config.hidden_size, intent_label_count
        )
        self.slot_classifier = nn.Linear(
            self.bert.config.hidden_size, slot_label_count
        )

    def forward(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass of the model.

        Args:
            input_ids: The input token IDs.
            attention_mask: The attention mask.

        Returns:
            Tuple of intent and slot logits.
        """
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        intent_logits = self.intent_classifier(outputs.pooler_output)
        slot_logits = self.slot_classifier(outputs.last_hidden_state)
        return intent_logits, slot_logits

    def predict(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[int, List[int]]:
        """Predicts the intent and slot annotations for the given input.

        Args:
            input_ids: The input token IDs.
            attention_mask (optional): The attention mask. Defaults to None.

        Returns:
            A tuple of the predicted intent and slot annotations.
        """
        if attention_mask is None:
            attention_mask = torch.ones(input_ids.shape)

        intent_logits, slot_logits = self(input_ids, attention_mask)

        predicted_intent = intent_logits.argmax(dim=1).item()
        predicted_slots = slot_logits.argmax(dim=2).squeeze()

        return predicted_intent, predicted_slots

    @classmethod
    def from_pretrained(cls, path: str) -> JointBERT:
        """Loads the model and tokenizer from the specified directory.

        Args:
            path: The path to the directory containing the model and tokenizer.

        Returns:
            The loaded model.
        """

        # Load the state dictionary
        model_path = os.path.join(path, "joint_bert_model.pth")
        state_dict = torch.load(model_path)

        # Infer label counts from the state dictionary
        intent_label_count = state_dict["intent_classifier.weight"].shape[0]
        slot_label_count = state_dict["slot_classifier.weight"].shape[0]

        # Create the model with inferred label counts
        model = cls(intent_label_count, slot_label_count)
        model.load_state_dict(state_dict)
        return model
