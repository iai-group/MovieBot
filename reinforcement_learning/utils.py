"""Utility functions."""
import logging
from typing import List

import confuse

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.domain.movie_domain import MovieDomain
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from usersimcrs.simulator.user_simulator import UserSimulator


def build_agenda_based_simulator(
    config: confuse.Configuration,
) -> UserSimulator:
    """Builds the agenda based user simulator.

    Args:
        config: Configuration for the simulation.

    Returns:
        Agenda based user simulator.
    """
    pass


def define_possible_actions(domain: MovieDomain) -> List[DialogueAct]:
    """Defines the possible agent actions.

    Args:
        domain: The movie domain.
    Returns:
        List of possible actions as dialogue acts.
    """
    actions = []
    actions += [
        DialogueAct(
            AgentIntents.ELICIT, [ItemConstraint(slot, Operator.EQ, "")]
        )
        for slot in domain.agent_requestable
    ]
    actions += [
        DialogueAct(
            AgentIntents.RECOMMEND,
        ),
        DialogueAct(
            AgentIntents.CONTINUE_RECOMMENDATION,
        ),
    ]
    actions.append(DialogueAct(AgentIntents.INFORM))
    actions.append(DialogueAct(AgentIntents.NO_RESULTS))
    actions.append(
        DialogueAct(
            AgentIntents.COUNT_RESULTS,
        )
    )
    actions.append(
        DialogueAct(
            AgentIntents.WELCOME,
            [
                ItemConstraint("new_user", Operator.EQ, "Placeholder"),
                ItemConstraint("is_bot", Operator.EQ, "Placeholder"),
            ],
        )
    )
    actions.append(DialogueAct(AgentIntents.WELCOME))
    actions.append(DialogueAct(AgentIntents.RESTART))
    actions.append(DialogueAct(AgentIntents.CANT_HELP))
    actions.append(DialogueAct(AgentIntents.BYE))
    return actions


def get_config(path: str, name: str) -> confuse.Configuration:
    """Loads a configuration file.

    Args:
        path: Path to the configuration file.
        name: Name of the configuration file.
    """
    config = confuse.Configuration(name, __name__)
    config.set_file(path)
    logging.info(f'Configuration file "{path}" is loaded.')
    return config
