"""Utility functions."""
import logging
from typing import List

import confuse
from usersimcrs.domain.simulation_domain import SimulationDomain
from usersimcrs.items.item_collection import ItemCollection
from usersimcrs.items.ratings import Ratings
from usersimcrs.simulator.agenda_based.interaction_model import (
    InteractionModel,
)
from usersimcrs.simulator.moviebot.moviebot_rl_sim import UserSimulatorMovieBot
from usersimcrs.simulator.user_simulator import UserSimulator
from usersimcrs.user_modeling.simple_preference_model import (
    SimplePreferenceModel,
)
from usersimcrs.utils.simulator_building import get_NLU

from dialoguekit.nlg.nlg_conditional import ConditionalNLG
from dialoguekit.nlg.template_from_training_data import (
    extract_utterance_template,
)
from dialoguekit.utils.dialogue_reader import json_to_dialogues
from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.domain.movie_domain import MovieDomain
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator


def build_agenda_based_simulator(
    config: confuse.Configuration,
) -> UserSimulator:
    """Builds the agenda based user simulator.

    Args:
        config: Configuration for the simulation.

    Returns:
        Agenda based user simulator.
    """
    domain = SimulationDomain(config["domain"].get())

    item_collection = ItemCollection()
    item_collection.load_items_csv(
        config["items"].get(),
        domain=domain,
        domain_mapping=config["domain_mapping"].get(),
        id_col=config["id_col"].get(),
    )

    ratings = Ratings(item_collection)
    ratings.load_ratings_csv(file_path=config["ratings"].get())
    historical_ratings, ground_truth_ratings = ratings.create_split(
        config["historical_ratings_ratio"].get(0.8)
    )

    preference_model = SimplePreferenceModel(
        domain,
        item_collection,
        historical_ratings,
        historical_user_id="13",
    )

    # Loads dialogue sample
    annotated_dialogues_file = config["dialogues"].get()
    annotated_conversations = json_to_dialogues(
        annotated_dialogues_file,
    )

    # Loads interaction model
    interaction_model = InteractionModel(
        config_file=config["intents"].get(),
        annotated_conversations=annotated_conversations,
    )

    # NLU
    nlu = get_NLU(config)

    # NLG
    template = extract_utterance_template(
        annotated_dialogue_file=annotated_dialogues_file,
    )
    for i, v in template.items():
        for utterance in v:
            if utterance.text == "Do you have something more recent?":
                v.remove(utterance)
        template[i] = v

    nlg = ConditionalNLG(template)

    return UserSimulatorMovieBot(
        config["simulator_id"].get(),
        preference_model,
        interaction_model,
        nlu,
        nlg,
        domain,
        item_collection,
        ratings,
    )


def define_possible_actions(domain: MovieDomain) -> List[DialogueAct]:
    """Defines the possible agent actions.

    Args:
        domain: The movie domain.
    Returns:
        List of possible actions as dialogue acts.
    """
    actions = [
        DialogueAct(AgentIntents.RECOMMEND),
        DialogueAct(AgentIntents.CONTINUE_RECOMMENDATION),
        DialogueAct(AgentIntents.INFORM),
        DialogueAct(AgentIntents.NO_RESULTS),
        DialogueAct(AgentIntents.COUNT_RESULTS),
        DialogueAct(
            AgentIntents.WELCOME,
            [
                ItemConstraint("new_user", Operator.EQ, "Placeholder"),
                ItemConstraint("is_bot", Operator.EQ, "Placeholder"),
            ],
        ),
        DialogueAct(AgentIntents.WELCOME),
        DialogueAct(AgentIntents.RESTART),
        DialogueAct(AgentIntents.CANT_HELP),
        DialogueAct(AgentIntents.BYE),
    ]
    actions += [
        DialogueAct(
            AgentIntents.ELICIT, [ItemConstraint(slot, Operator.EQ, "")]
        )
        for slot in domain.agent_requestable
    ]
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
