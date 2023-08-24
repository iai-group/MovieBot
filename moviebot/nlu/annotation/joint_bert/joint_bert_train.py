import json
import os

import pytorch_lightning as pl
import torch
import torch.nn as nn
import torch.nn.functional as F
from pytorch_lightning.loggers import WandbLogger
from torch.optim import SGD
from torch.utils.data import DataLoader
from transformers import AdamW, BertTokenizer, get_linear_schedule_with_warmup

from moviebot.nlu.annotation.joint_bert.snips import JointBERTDataset

from .joint_bert import JointBERT

# from moviebot.nlu.annotation.joint_bert.slot_mapping import (
#     JointBERTIntent,
#     JointBERTSlot,
# )


_MODEL_OUTPUT_PATH = "moviebot/nlu/annotation/joint_bert/snips_model"
# _DATA_PATH = "data/training/utterances_chatGPT_clean.yaml"

_IGNORE_INDEX = -100
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


class JointBERTTrain(JointBERT, pl.LightningModule):
    def __init__(
        self, intent_label_count, slot_label_count, learning_rate=5e-5
    ):
        super(JointBERTTrain, self).__init__(
            intent_label_count, slot_label_count
        )
        self.learning_rate = learning_rate
        self.slot_loss_fct = nn.CrossEntropyLoss(ignore_index=_IGNORE_INDEX)

    def on_train_batch_start(self, batch, batch_idx):
        if batch_idx == 10:
            self.initial_weights = self.intent_classifier.weight.clone()
            print(self.initial_weights)

    def on_train_batch_end(self, outputs, batch, batch_idx):
        if batch_idx == 10:
            for name, param in self.named_parameters():
                if (
                    "intent_classifier" in name or "slot_classifier" in name
                ) and param.requires_grad:
                    print(name, param.grad)
            weight_diff = self.intent_classifier.weight - self.initial_weights
            print(
                f"Weight updates for the intent classifier layer in batch {batch_idx}:"
            )
            print(self.intent_classifier.weight)
            print(weight_diff)

    def training_step(self, batch, batch_idx):
        input_ids, attention_mask, intent_labels, slot_labels = batch
        relevant_labels = slot_labels.view(-1) != _IGNORE_INDEX

        intent_logits, slot_logits = self(input_ids, attention_mask)
        loss_intent = F.cross_entropy(
            intent_logits.view(-1, self.intent_label_count),
            intent_labels.view(-1),
        )
        # loss_slot = F.cross_entropy(
        #     slot_logits.view(-1, self.slot_label_count),
        #     slot_labels.view(-1),
        #     ignore_index=_IGNORE_INDEX,
        # )
        loss_slot = F.cross_entropy(
            slot_logits.view(-1, self.slot_label_count)[relevant_labels],
            slot_labels.view(-1)[relevant_labels],
        )
        loss = loss_intent + loss_slot
        # Debugging: Print shapes and values of important variables
        # if batch_idx % 20 == 0:  # Print every 10 batches
        #     print("Batch:", batch_idx)
        #     print("loss_slot_1", loss_slot)
        #     print(
        #         "loss_slot_2",
        #         F.cross_entropy(
        #             slot_logits.view(-1, self.slot_label_count),
        #             slot_labels.view(-1),
        #             ignore_index=-99,
        #         ),
        #     )
        #     loss_3 = F.cross_entropy(
        #         slot_logits.view(-1, self.slot_label_count)[relevant_labels],
        #         slot_labels.view(-1)[relevant_labels],
        #     )
        #     print("loss_slot_3", loss_3)
        #     print(
        #         "loss_4",
        #         self.slot_loss_fct(
        #             slot_logits.view(-1, self.slot_label_count),
        #             slot_labels.view(-1),
        #         ),
        #     )

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
        return loss

    def validation_step(self, batch, batch_idx):
        input_ids, attention_mask, intent_labels, slot_labels = batch
        intent_logits, slot_logits = self(input_ids, attention_mask)

        # Compute the loss for intent and slot predictions
        loss_intent = F.cross_entropy(
            intent_logits.view(-1, self.intent_label_count),
            intent_labels.view(-1),
        )
        loss_slot = F.cross_entropy(
            slot_logits.view(-1, self.slot_label_count),
            slot_labels.view(-1),
            ignore_index=_IGNORE_INDEX,
        )
        val_loss = loss_intent + loss_slot

        # Optionally, compute additional metrics
        intent_acc = (
            (intent_logits.argmax(dim=1) == intent_labels).float().mean()
        )
        slot_acc = (
            (
                (slot_logits.argmax(dim=2) == slot_labels)
                & (slot_labels != _IGNORE_INDEX)
            )
            .float()
            .mean()
        )

        # Log the metrics
        self.log(
            "val_loss",
            val_loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        self.log(
            "intent_acc",
            intent_acc,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )
        self.log(
            "slot_acc",
            slot_acc,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            logger=True,
        )

        return val_loss

    def configure_optimizers(self):
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [
                    p
                    for n, p in self.named_parameters()
                    if not any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,  # self.args.weight_decay,
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
        # optimizer = AdamW(optimizer_grouped_parameters, lr=self.learning_rate)
        optimizer = SGD(self.parameters(), lr=self.learning_rate)
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=self.trainer.max_steps,
        )
        return optimizer

    def save_pretrained(self, path: str) -> None:
        """Saves the model to the specified directory."""

        if not os.path.exists(path):
            os.makedirs(path)

        model_path = os.path.join(path, "joint_bert_model.pth")
        torch.save(self.state_dict(), model_path)

        # Save metadata
        # metadata = {
        #     "intents": [intent.name for intent in JointBERTIntent],
        #     "slots": [slot.name for slot in JointBERTSlot],
        # }
        metadata_path = os.path.join(path, "metadata.json")
        # with open(metadata_path, "w") as f:
        #     json.dump(metadata, f)


def print_weights(model):
    for name, param in model.named_parameters():
        if (
            "intent_classifier" in name or "slot_classifier" in name
        ) and param.requires_grad:
            print(
                name,
                param.data.mean(),
                param.data.std(),
                param.data.min(),
                param.data.max(),
            )


def check_grad_requirements(model):
    for name, param in model.named_parameters():
        print(name, "requires_grad:", param.requires_grad)


if __name__ == "__main__":
    dataset = JointBERTDataset("train")
    validation = JointBERTDataset("valid")
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True, num_workers=4)
    val_dataloader = DataLoader(validation, batch_size=64, num_workers=4)
    model = JointBERTTrain(
        intent_label_count=dataset.intent_label_count,
        slot_label_count=dataset.slot_label_count,
    )

    # wandb_logger = WandbLogger(project="JointBERT")

    # check_grad_requirements(model)
    print_weights(model)

    trainer = pl.Trainer(max_epochs=1)  # , logger=wandb_logger)
    # trainer = pl.Trainer(max_epochs=10, logger=wandb_logger)
    trainer.fit(model, dataloader, val_dataloader)

    print_weights(model)

    # Save model
    model.save_pretrained(_MODEL_OUTPUT_PATH)
    print(f"Model saved to {_MODEL_OUTPUT_PATH}")
