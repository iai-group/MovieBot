"""Mapping of slot and intent labels to indices for JointBERT model."""
from __future__ import annotations

from enum import Enum, auto


class EnumWithMapping(Enum):
    @classmethod
    def to_index(cls, name: str) -> int:
        return cls[name.upper()].value - 1

    @classmethod
    def from_index(cls, index: int) -> EnumWithMapping:
        return cls(index + 1)


class JointBERTIntent(EnumWithMapping):
    REVEAL = auto()
    INQUIRE = auto()
    REMOVE_PREFERENCE = auto()
    REJECT = auto()
    ACCEPT = auto()
    CONTINUE_RECOMMENDATION = auto()
    RESTART = auto()
    UNK = auto()
    ACKNOWLEDGE = auto()
    DENY = auto()
    HI = auto()
    BYE = auto()


class JointBERTSlot(EnumWithMapping):
    OUT = auto()
    B_PREFERENCE_MODIFIER = auto()
    I_PREFERENCE_MODIFIER = auto()
    B_PREFERENCE_MODIFIER_YEAR = auto()
    I_PREFERENCE_MODIFIER_YEAR = auto()
    B_PREFERENCE_GENRES = auto()
    I_PREFERENCE_GENRES = auto()
    B_PREFERENCE_ACTORS = auto()
    I_PREFERENCE_ACTORS = auto()
    B_PREFERENCE_DIRECTORS = auto()
    I_PREFERENCE_DIRECTORS = auto()
    B_PREFERENCE_KEYWORDS = auto()
    I_PREFERENCE_KEYWORDS = auto()
    B_PREFERENCE_YEAR = auto()
    I_PREFERENCE_YEAR = auto()
    B_INQUIRE_GENRES = auto()
    I_INQUIRE_GENRES = auto()
    B_INQUIRE_RATING = auto()
    I_INQUIRE_RATING = auto()
    B_INQUIRE_DURATION = auto()
    I_INQUIRE_DURATION = auto()
    B_INQUIRE_PLOT = auto()
    I_INQUIRE_PLOT = auto()
    B_INQUIRE_ACTORS = auto()
    I_INQUIRE_ACTORS = auto()
    B_INQUIRE_DIRECTORS = auto()
    I_INQUIRE_DIRECTORS = auto()
    B_INQUIRE_YEAR = auto()
    I_INQUIRE_YEAR = auto()

    def is_start(self) -> bool:
        """Returns True if the slot is a starting point for a slot value."""
        return "B_" in self.name

    def is_inside(self) -> bool:
        """Returns True if the slot is inside a slot value."""
        return "I_" in self.name


if __name__ == "__main__":
    print(JointBERTIntent.to_index("REVEAL"))
    print(JointBERTIntent.from_index(0))
    print(JointBERTSlot.to_index("B_PREFERENCE_MODIFIER"))
    print(JointBERTSlot.from_index(1))
