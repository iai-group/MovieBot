"""Training script for the JointBERT model."""

import argparse
import json
import os
from typing import List, Tuple

import pytorch_lightning as pl
import torch
import torch.nn.functional as F
from pytorch_lightning.loggers import WandbLogger
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup

from moviebot.nlu.annotation.joint_bert import JointBERT
from moviebot.nlu.annotation.joint_bert.dataset import (
    _IGNORE_INDEX,
    JointBERTDataset,
)
from moviebot.nlu.annotation.joint_bert.slot_mapping import (
    JointBERTIntent,
    JointBERTSlot,
)

Batch = Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]

_MODEL_OUTPUT_PATH = "models/joint_bert"
_DATA_PATH = "data/training/utterances.yaml"


class JointBERTTrain(JointBERT, pl.LightningModule):
    def __init__(
        self, intent_label_count: int, slot_label_count: int, **kwargs
    ) -> None:
        """Initializes the JointBERT training model.

        Args:
            intent_label_count: Number of intent labels to classify.
            slot_label_count: Number of slot labels to classify.
        """
        super(JointBERTTrain, self).__init__(
            intent_label_count, slot_label_count
        )
        self.save_hyperparameters()

    def _calculate_losses(
        self, batch: Batch
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Calculates losses for a batch.

        Args:
            batch: A batch of data.

        Returns:
            Tuple of intent and slot losses.
        """
        input_ids, attention_mask, intent_labels, slot_labels = batch
        relevant_labels = slot_labels.view(-1) != _IGNORE_INDEX

        intent_logits, slot_logits = self(input_ids, attention_mask)

        loss_intent = F.cross_entropy(
            intent_logits.view(-1, self.intent_label_count),
            intent_labels.view(-1),
        )
        loss_slot = F.cross_entropy(
            slot_logits.view(-1, self.slot_label_count)[relevant_labels],
            slot_labels.view(-1)[relevant_labels],
        )
        return loss_intent, loss_slot

    def training_step(self, batch: Batch, batch_idx: int) -> torch.Tensor:
        """Training step for the JointBERT model.

        Args:
            batch: A batch of data.
            batch_idx: Index of the batch.

        Returns:
            The loss for the batch.
        """
        loss_intent, loss_slot = self._calculate_losses(batch)

        self.log(
            "train_loss_intent",
            loss_intent,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        self.log(
            "train_loss_slot",
            loss_slot,
            on_step=True,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        return loss_intent + loss_slot

    def validation_step(self, batch: Batch, batch_idx: int) -> torch.Tensor:
        """Validation step for the JointBERT model.

        Args:
            batch: A batch of data.
            batch_idx: Index of the batch.

        Returns:
            The loss for the batch.
        """
        loss_intent, loss_slot = self._calculate_losses(batch)
        val_loss = loss_intent + loss_slot

        # Log the metrics
        self.log(
            "val_loss",
            val_loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )

        return val_loss

    def configure_optimizers(self) -> Tuple[List, List]:
        """Configures the optimizer and scheduler for training."""
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [
                    p
                    for n, p in self.named_parameters()
                    if not any(nd in n for nd in no_decay)
                ],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [
                    p
                    for n, p in self.named_parameters()
                    if any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,
            },
        ]
        optimizer = torch.optim.AdamW(
            optimizer_grouped_parameters, lr=self.hparams.learning_rate
        )

        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=self.hparams.max_steps,
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


def parse_arguments():
    """Parses the command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_output_path", type=str, default=_MODEL_OUTPUT_PATH
    )
    parser.add_argument("--data_path", type=str, default=_DATA_PATH)
    parser.add_argument("--max_epochs", type=int, default=5)
    parser.add_argument("--learning_rate", type=float, default=5e-5)
    parser.add_argument("--weight_decay", type=float, default=0.0)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()
    wandb_logger = WandbLogger(project="JointBERT")

    dataset = JointBERTDataset(args.data_path)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=4)

    model = JointBERTTrain(
        intent_label_count=dataset.intent_label_count,
        slot_label_count=dataset.slot_label_count,
        learning_rate=args.learning_rate,
        max_steps=len(dataloader) * args.max_epochs,
        weight_decay=args.weight_decay,
    )

    trainer = pl.Trainer(max_epochs=args.max_epochs, logger=wandb_logger)
    trainer.fit(model, dataloader)

    model.save_pretrained(args.model_output_path)
    dataset.tokenizer.save_pretrained(args.model_output_path)
    print(f"Model saved to {args.model_output_path}")
