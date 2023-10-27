import gymnasium as gym

from reinforcement_learning.environment.dialogue_env_moviebot import (
    DialogueEnvMovieBot,
)
from reinforcement_learning.environment.dialogue_env_moviebot_no_nlu import (
    DialogueEnvMovieBotNoNLU,
)

__all__ = [
    "DialogueEnvMovieBot",
    "DialogueEnvMovieBotNoNLU",
]

gym.register(
    id="DialogueEnvMovieBot-v0",
    entry_point="reinforcement_learning.environment.dialogue_env_moviebot:DialogueEnvMovieBot",  # noqa: E501
)

gym.register(
    id="DialogueEnvMovieBotNoNLU-v0",
    entry_point=(
        "reinforcement_learning.environment.dialogue_env_moviebot_no_nlu:DialogueEnvMovieBotNoNLU"  # noqa: E501
    ),
)
