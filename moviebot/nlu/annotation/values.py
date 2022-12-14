"""This file contains the list of possible slot values other than the values
fetched from the database.
This approach will help the dialogue state tracker to update state for specific
type of slot values easily"""


from enum import Enum


class Values(Enum):
    """This class contains the list of possible slot values other than the
    values fetched from the database. This approach will help the dialogue state
    tracker to update state for specific type of slot values easily"""

    DONT_CARE = "dont_care"
    DISCLOSE_NOT = "disclose_not"
    NOT_FOUND = "not_found"

    def __str__(self):
        return str(self.value)
