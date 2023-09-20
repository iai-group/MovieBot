"""Class representing domain knowledge."""


import logging

from dialoguekit.core import Domain

logger = logging.getLogger(__name__)


class MovieDomain(Domain):
    def __init__(self, config_file: str) -> None:
        """Initializes the internal structures of the domain.

        Args:
            path: Path to YAML config file.
        """
        super().__init__(config_file)

        self.agent_requestable = []
        self.user_requestable = []
        self.slots_not_required_NLU = []
        self.slots_annotation = []
        self.multiple_values_CIN = []

        for slot, properties in self._config.get("slot_names").items():
            if "system_requestable" in properties:
                self.agent_requestable.append(slot)
            if "user_requestable" in properties:
                self.user_requestable.append(slot)
            if "slots_not_required_NLU" in properties:
                self.slots_not_required_NLU.append(slot)
            if "slots_annotation" in properties:
                self.slots_annotation.append(slot)
            if "multiple_values" in properties:
                self.multiple_values_CIN.append(slot)
