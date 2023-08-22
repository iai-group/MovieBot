import json
import os

import pytorch_lightning as pl
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import AdamW, get_linear_schedule_with_warmup

from moviebot.nlu.annotation.joint_bert.dataset import JointBERTDataset
from moviebot.nlu.annotation.joint_bert.slot_mapping import (
    JointBERTIntent,
    JointBERTSlot,
)

from .joint_bert import JointBERT

_MODEL_OUTPUT_PATH = "moviebot/nlu/annotation/joint_bert/model"
_DATA_PATH = "data/training/utterances_chatGPT_clean.yaml"

_IGNORE_INDEX = -100


class JointBERTTrain(JointBERT, pl.LightningModule):
    def __init__(
        self, intent_label_count, slot_label_count, learning_rate=5e-2
    ):
        super(JointBERTTrain, self).__init__(
            intent_label_count, slot_label_count
        )
        self.learning_rate = learning_rate

    def training_step(self, batch, batch_idx):
        input_ids, attention_mask, intent_labels, slot_labels = batch
        intent_logits, slot_logits = self(input_ids, attention_mask)
        loss_intent = F.cross_entropy(
            intent_logits.view(-1, self.intent_label_count),
            intent_labels.view(-1),
        )
        loss_slot = F.cross_entropy(
            slot_logits.view(-1, self.slot_label_count),
            slot_labels.view(-1),
            ignore_index=_IGNORE_INDEX,
        )
        loss = loss_intent + loss_slot
        self.log(
            "train_loss",
            loss,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        return loss

    def configure_optimizers(self):
        optimizer = AdamW(
            self.parameters(), lr=self.learning_rate, correct_bias=False
        )
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=self.trainer.max_steps,
        )
        return [optimizer], [scheduler]

    def save_pretrained(self, path: str) -> None:
        """Saves the model to the specified directory."""

        if not os.path.exists(path):
            os.makedirs(path)

        model_path = os.path.join(path, "joint_bert_model.pth")
        torch.save(self.state_dict(), model_path)

        # Save metadata
        metadata = {
            "intents": [intent.name for intent in JointBERTIntent],
            "slots": [slot.name for slot in JointBERTSlot],
        }
        metadata_path = os.path.join(path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)


dataset = JointBERTDataset(_DATA_PATH)
dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
model = JointBERTTrain(
    intent_label_count=len(JointBERTIntent), slot_label_count=len(JointBERTSlot)
)
trainer = pl.Trainer(max_epochs=3)
trainer.fit(model, dataloader)

# Save model
model.save_pretrained(_MODEL_OUTPUT_PATH)
print(f"Model saved to {_MODEL_OUTPUT_PATH}")
