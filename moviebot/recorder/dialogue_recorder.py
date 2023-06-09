"""Records the dialogue details of the conversation in it's raw form."""

import datetime
import json
import os
from collections import defaultdict
from typing import Any, Dict, List

from moviebot.dialogue_manager.dialogue_act import DialogueAct


class DialogueRecorder:
    def __init__(self, path: str, nlp: bool) -> None:
        """Initializes the recorder.

        If required, it also saves the dialogue acts.

        Args:
            path: Path to the save file.
            nlp: If true, the Dialogue Acts will also be saved.
        """
        self.path = path
        self.nlp = nlp

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.conversations = defaultdict(list)

    def record(
        self,
        user_name: str,
        text: str,
        dialogue_acts: List[DialogueAct],
        participant: str,
    ) -> None:
        """Records the current dialogue utterance.

        Args:
            user_name: Name of the user.
            text: Text.
            dialogue_acts: Dialogue acts.
            participant: Type of interlocutor, i.e., AGENT or USER.
        """
        intents = []
        slot_values = []
        for dact in dialogue_acts:
            intents.append(dact.intent.name)
            for constraint in dact.params:
                slot_values.append([constraint.slot, constraint.value])

        utterance = {
            "utterance": text,
            "participant": participant,
        }
        if self.nlp:
            utterance["intents"] = intents
            utterance["slot_values"] = slot_values
        self.conversations[user_name].append(utterance)

    def _conversation_to_dict(
        self, user_name: str, utterances: list
    ) -> Dict[str, Any]:
        """Converts a conversation to a dictionary.

        Args:
            user_name: Name of the user.
            utterances: List of utterances.
        """
        return {
            "conversation ID": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "conversation": utterances,
            "user": user_name,
            "agent": "IAI MovieBot",
        }

    def save(self) -> None:
        """Saves all the dialogues in the conversation to a file."""
        conversations = []
        for user_name, conversation in self.conversations.items():
            conversations.append(
                self._conversation_to_dict(user_name, conversation)
            )

        output_file = os.path.join(self.path, "dialogues.json")
        try:
            with open(output_file, "r") as f:
                data = json.load(f)
                conversations.extend(data)
        except FileNotFoundError:
            pass
        finally:
            with open(output_file, "w") as f:
                json.dump(conversations, f, indent=4)
