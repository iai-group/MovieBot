from typing import Optional, Tuple

from transformers import BertTokenizerFast

from moviebot.agent.agent import DialogueOptions
from moviebot.core.intents import UserIntents
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.joint_bert import JointBERT
from moviebot.nlu.annotation.joint_bert.slot_mapping import (
    JointBERTIntent,
    JointBERTSlot,
)
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.slots import Slots
from moviebot.nlu.nlu import NLU

_DEFAULT_MODEL_PATH = "moviebot/nlu/annotation/joint_bert/model"


class NeuralNLU(NLU):
    def __init__(self, path: Optional[str] = _DEFAULT_MODEL_PATH) -> None:
        self._model = JointBERT.from_pretrained(path)
        self._tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")

    def generate_dact(
        self,
        user_utterance: UserUtterance,
        options: DialogueOptions = None,
        dialogue_state: DialogueState = None,
    ):
        """Processes the utterance according to dialogue state and generate a
        user dialogue act for Agent to understand.

        Args:
            user_utterance: UserUtterance class containing user input.
            options: A list of options provided to the user to choose from.
            dialogue_state: The current dialogue state, if available. Defaults
                to None.

        Returns:
            A list of dialogue acts.
        """
        selected_option = self._get_selected_option(
            user_utterance, options, dialogue_state.item_in_focus
        )
        if selected_option:
            return selected_option

        intent, slots = self.annotate_utterance(user_utterance)

        constraints = []
        operator = None
        for slot in slots.items():
            if slot["slot"] == "MODIFIER":
                operator = self.get_operator(slot["value"])
                continue
            constraints.append(
                ItemConstraint(
                    Slots(slot=slot["slot"]),
                    op=operator or Operator.EQ,
                    value=slot["value"],
                )
            )

        return [DialogueAct(UserIntents[intent], constraints)]

    def annotate_utterance(
        self, user_utterance: UserUtterance
    ) -> Tuple[str, list]:
        """Annotates the utterance with intent and slot information.

        Args:
            user_utterance: UserUtterance class containing user input.

        Returns:
            A tuple of the intent and slot information.
        """
        mask = [
            not token.startswith("##")
            for token in self._tokenizer.tokenize(user_utterance.text)
        ]
        encoding = self._tokenizer.encode_plus(
            user_utterance.text,
            return_offsets_mapping=True,
            add_special_tokens=True,
            return_tensors="pt",
        )
        intent_idx, slot_idxs = self._model.predict(encoding["input_ids"])

        # [1:-1] to remove [CLS] and [SEP] tokens
        offset_mapping = encoding["offset_mapping"][0, 1:-1][mask].tolist()
        slot_idxs = slot_idxs[1:-1][mask]

        # Identify starting points for slots (i.e., 'B_' labels)
        start_indices = [
            i
            for i, idx in enumerate(slot_idxs)
            if JointBERTSlot.from_index(idx).is_start()
        ]

        # For each starting point, find the end point (i.e., all 'I_' labels)
        slots_info = []
        for start in start_indices:
            end = start
            while (
                end + 1 < len(slot_idxs)
                and JointBERTSlot.from_index(slot_idxs[end + 1]).is_inside()
            ):
                end += 1

            char_start = offset_mapping[start][0]
            char_end = offset_mapping[end][1]
            slot_value = user_utterance.text[char_start:char_end]
            slots_info.append(
                {
                    "slot": JointBERTSlot.from_index(slot_idxs[start]).name[2:],
                    "value": slot_value,
                    "start": char_start,
                    "end": char_end,
                }
            )

        return JointBERTIntent.from_index(intent_idx).name, slots_info

    def get_operator(self, text: str) -> Operator:
        """Gets the operator based on the text.

        Args:
            text: The text to analyze.

        Returns:
            The operator.
        """
        return Operator.EQ


if __name__ == "__main__":
    nlu = NLU()

    while True:
        text = input("Enter text: ")
        predicted_intent, predicted_slots = nlu.generate_dact(
            UserUtterance(text)
        )

        print(text)
        print(predicted_intent)
        print(predicted_slots)
