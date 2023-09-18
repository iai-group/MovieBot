"""Core types for the moviebot package."""
from typing import TYPE_CHECKING, Dict, List, Union

if TYPE_CHECKING:
    from moviebot.dialogue_manager.dialogue_act import DialogueAct

DialogueOptions = Dict["DialogueAct", Union[str, List[str]]]
