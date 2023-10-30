"""Utils for building simulator."""
import confuse
from dialoguekit.nlu import NLU
from dialoguekit.nlu.intent_classifier import IntentClassifier
from dialoguekit.nlu.models.diet_classifier_rasa import IntentClassifierRasa
from dialoguekit.nlu.models.intent_classifier_cosine import (
    IntentClassifierCosine,
)
import json
from dialoguekit.core.intent import Intent

from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.participant import DialogueParticipant
import yaml
from typing import Set


def get_NLU(config: confuse.Configuration) -> IntentClassifier:
    """Returns an NLU component.

    Only supports DialogueKit intent classifiers.

    Args:
        config: Configuration for the simulation.

    Raises:
        ValueError: Unsupported intent classifier.

    Returns:
        An NLU component.
    """

    intent_classifier = config["intent_classifier"].get()
    if intent_classifier == "cosine":
        # NLU without slot annotators
        return NLU(load_cosine_classifier(config), slot_annotators=[])
    elif intent_classifier == "diet":
        classifier = load_rasa_diet_classifier(config)
        return NLU(classifier, [classifier])
    elif intent_classifier:
        raise ValueError(
            "Unsupported intent classifier. Check DialogueKit intent"
            " classifiers."
        )


def load_cosine_classifier(
    config: confuse.Configuration,
) -> IntentClassifierCosine:
    """Trains a cosine classifier on annotated dialogues for NLU module.

    Args:
        config: Configuration generated from YAML configuration file.

    Returns:
        A trained cosine model for intent classification.
    """
    # TODO: Move to DialogueKit as util function.
    # See: https://github.com/iai-group/UserSimCRS/issues/92
    annotated_dialogues_file = config["dialogues"].get()
    dialogues = json.load(open(annotated_dialogues_file))

    gt_intents = []
    utterances = []
    for conversation in dialogues:
        for turn in conversation["conversation"]:
            if turn["participant"] == "AGENT":
                gt_intents.append(Intent(turn["intent"]))
                utterances.append(
                    Utterance(
                        turn["utterance"],
                        participant=DialogueParticipant.AGENT,
                    )
                )
    intent_classifier = IntentClassifierCosine(intents=gt_intents)
    intent_classifier.train_model(utterances=utterances, labels=gt_intents)
    return intent_classifier


def load_rasa_diet_classifier(
    config: confuse.Configuration,
) -> IntentClassifierCosine:
    """Trains a DIET classifier on Rasa annotated dialogues for NLU module.

    Args:
        config: Configuration generated from YAML configuration file.

    Returns:
        A trained Rasa DIET model for intent classification.
    """
    # TODO: Move to DialogueKit as util function.
    # See: https://github.com/iai-group/UserSimCRS/issues/92
    intent_schema_file = config["intents"].get()
    intent_schema = yaml.load(open(intent_schema_file), Loader=yaml.FullLoader)

    agent_intents_str: Set[str] = set()
    for v in intent_schema["user_intents"].values():
        intents = v.get("expected_agent_intents", []) or []
        agent_intents_str.update(intents)
    # agent_intents_str = intent_schema["agent_elicit_intents"]
    # agent_intents_str.extend(intent_schema["agent_set_retrieval"])
    agent_intents = [Intent(intent) for intent in agent_intents_str]
    agent_intents.append(Intent("FAILED"))
    intent_classifier = IntentClassifierRasa(
        agent_intents,
        config["rasa_dialogues"].get(),
        "rasa_conversations23",
    )
    intent_classifier.train_model()
    return intent_classifier
