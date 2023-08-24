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
    B_MODIFIER = auto()
    I_MODIFIER = auto()
    B_GENRE = auto()
    I_GENRE = auto()
    B_ACTOR = auto()
    I_ACTOR = auto()
    B_DIRECTOR = auto()
    I_DIRECTOR = auto()
    B_KEYWORD = auto()
    I_KEYWORD = auto()
    B_YEAR = auto()
    I_YEAR = auto()

    def is_start(self) -> bool:
        """Returns True if the slot is a starting point for a slot value."""
        return "B_" in self.name

    def is_inside(self) -> bool:
        """Returns True if the slot is inside a slot value."""
        return "I_" in self.name


if __name__ == "__main__":
    print(JointBERTIntent.to_index("REVEAL"))
    print(JointBERTIntent.from_index(0))
    print(JointBERTSlot.to_index("B_MODIFIER"))
    print(JointBERTSlot.from_index(1))
