"""The Operator class defines acceptable operators.
It will be used to identify dialogue act item operator
"""


from enum import Enum


class Operator(Enum):
    """The Operator class defines acceptable operators.
    It will be used to identify dialogue act item operator"""

    EQ = 1
    NE = 2
    LT = 3
    LE = 4
    GT = 5
    GE = 6
    AND = 7
    OR = 8
    NOT = 9
    IN = 10
    BETWEEN = 11

    def __str__(self) -> str:
        """Returns a string representation of the Operator."""
        opr = "UNK"
        if self.name == "EQ":
            opr = "="
        elif self.name == "NE":
            opr = "!="
        elif self.name == "LT":
            opr = "<"
        elif self.name == "LE":
            opr = "<="
        elif self.name == "GT":
            opr = ">"
        elif self.name == "GE":
            opr = ">="
        elif self.name in ["AND", "OR", "NOT", "IN", "BETWEEN"]:
            opr = self.name

        return opr
