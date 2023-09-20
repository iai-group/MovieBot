from typing import Any, Dict, List, Optional, Tuple

from transformers import BertTokenizerFast

from moviebot.core.core_types import DialogueOptions
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
from moviebot.nlu.user_intents_checker import PATTERN_DONT_WANT

_DEFAULT_MODEL_PATH = "models/joint_bert"


class NeuralNLU(NLU):
    def __init__(
        self, config: Dict[str, Any], path: Optional[str] = _DEFAULT_MODEL_PATH
    ) -> None:
        """The NeuralNLU class.

        Args:
            config: Paths to domain, database and tag words for slots in NLU.
            path: Path to the model. Defaults to _DEFAULT_MODEL_PATH.
        """
        super().__init__(config)
        self._model = JointBERT.from_pretrained(path)
        self._tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")

    def generate_dacts(
        self,
        user_utterance: UserUtterance,
        options: DialogueOptions = None,
        dialogue_state: DialogueState = None,
    ) -> List[DialogueAct]:
        """Processes the utterance according to dialogue state and generate a
        user dialogue act for Agent to understand.

        Args:
            user_utterance: User utterance class containing user input.
            options: A list of options provided to the user to choose from.
                Defaults to None.
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
        intent = UserIntents[intent]

        constraints = []
        operator = None
        for slot in slots:
            if "MODIFIER" in slot["slot"]:
                operator = self.get_constraint_operator(slot["value"])
                continue

            if intent == UserIntents.INQUIRE and "INQUIRE" not in slot["slot"]:
                continue
            if (
                intent in (UserIntents.REMOVE_PREFERENCE, UserIntents.INQUIRE)
                and "PREFERENCE" not in slot["slot"]
            ):
                continue
            slot_name = Slots[slot["slot"].split("_")[-1]].value
            constraints.append(
                ItemConstraint(
                    slot_name,
                    op=operator or Operator.EQ,
                    value=slot["value"],
                )
            )

        return [DialogueAct(intent, constraints)]

    def annotate_utterance(
        self, user_utterance: UserUtterance
    ) -> Tuple[str, list]:
        """Annotates the utterance with intent and slot information.

        Args:
            user_utterance: User utterance class containing user input.

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
        intent = JointBERTIntent.from_index(intent_idx).name

        # [1:-1] to remove [CLS] and [SEP] tokens
        offset_mapping = encoding["offset_mapping"][0, 1:-1][mask].tolist()
        slot_idxs = slot_idxs[1:-1][mask].tolist()

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

        return intent, slots_info

    def get_constraint_operator(self, text: str) -> Operator:
        """Gets the operator based on the text. Only supports negation for now.

        Args:
            text: The text to analyze.

        Returns:
            The operator.
        """
        negation = any(phrase in text for phrase in PATTERN_DONT_WANT)
        return Operator.NE if negation else Operator.EQ


if __name__ == "__main__":
    nlu = NeuralNLU(None)

    class DS:
        item_in_focus = None

    while True:
        text = input("Enter text: ")
        da = nlu.generate_dacts(
            UserUtterance(text), options={}, dialogue_state=DS()
        )

        print([str(da) for da in da])
