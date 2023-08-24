from typing import Optional

from transformers import BertTokenizerFast

from moviebot.agent.agent import DialogueOptions
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.joint_bert import JointBERT
from moviebot.nlu.annotation.joint_bert.slot_mapping import (
    JointBERTIntent,
    JointBERTSlot,
)

_DEFAULT_MODEL_PATH = "moviebot/nlu/annotation/joint_bert/model"


class NLU:
    def __init__(self, path: Optional[str] = _DEFAULT_MODEL_PATH) -> None:
        self._model = JointBERT.from_pretrained(path)
        self._tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")

    def generate_dact(
        self,
        user_utterance: UserUtterance,
        options: DialogueOptions = None,
        dialogue_state: DialogueState = None,
    ):
        encoding = self._tokenizer.encode_plus(
            user_utterance.text,
            return_offsets_mapping=True,
            add_special_tokens=True,
            return_tensors="pt",
        )
        intent_idx, slot_idxs = self._model.predict(encoding["input_ids"])

        # Convert the text to BERT tokens, keeping track of token to original
        # char mapping
        offset_mapping = encoding["offset_mapping"][0][1:-1].tolist()
        slot_idxs = slot_idxs[1:-1]

        # Identify starting points for slots (i.e., 'B_' labels)
        start_indices = [
            i
            for i, idx in enumerate(slot_idxs)
            if JointBERTSlot.from_index(idx).is_start()
        ]

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

        print(
            intent_idx, slot_idxs, self._tokenizer.tokenize(user_utterance.text)
        )
        return JointBERTIntent.from_index(intent_idx).name, slots_info


if __name__ == "__main__":
    nlu = NLU()

    for t in [
        "I like action movies",
        "Hello, how are you doing?",
    ]:
        predicted_intent, predicted_slots = nlu.generate_dact(UserUtterance(t))

        print(t)
        print(predicted_intent)
        print(predicted_slots)
