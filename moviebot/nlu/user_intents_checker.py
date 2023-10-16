"""This file contains the main functions for checking the user intents."""

import re
import string
from copy import deepcopy
from typing import Any, Dict, List

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from moviebot.core.intents.user_intents import UserIntents
from moviebot.core.utterance.utterance import UserUtterance
from moviebot.database.db_movies import DataBase
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.domain.movie_domain import MovieDomain
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.rule_based_annotator import RBAnnotator
from moviebot.nlu.annotation.slots import Slots
from moviebot.nlu.annotation.values import Values
from moviebot.nlu.data_loader import DataLoader
from moviebot.nlu.recommendation_decision_processing import (
    RecommendationChoices,
    convert_choice_to_preference,
)

PATTERN_BASIC = {
    UserIntents.ACKNOWLEDGE: ["yes", "okay", "fine", "sure"],
    UserIntents.DENY: ["no", "nope", "nah", "not"],
    UserIntents.HI: ["hi", "hello", "hey", "howdy"],
    UserIntents.BYE: ["bye", "goodbye", "quit", "exit"],
}

PATTERN_DONT_CARE = [
    "anything",
    "any",
    "dont know",
    "i do not care",
    "i dont care",
    "dont care",
    "dontcare",
    "it does not matter",
    "it doesnt matter",
    "does not matter",
    "doesnt matter",
    "no one",
    "no body",
    "nobody",
    "nothing",
    "none",
]
PATTERN_QUESTION = [
    "who",
    "what",
    "when",
    "which",
    "can",
    "could",
    "is",
    "are",
]
PATTERN_DONT_LIKE = [
    "something else",
    "anything else",
    "dont like it",
    "not this",
    "another",
]
PATTERN_DONT_WANT = [
    "dont",
    "not",
    "nothing",
    "wont",
    "shouldnt",
    "dont need",
    "dont want",
    "no",
    "not",
]
PATTERN_WATCHED = [
    "watched",
    "seen",
    "yes",
    "I have",
    "yup",
    "yea",
]


class UserIntentsChecker:
    def __init__(self, config: Dict[str, Any]) -> None:
        """CheckUserIntents is a class to detect the intents for the class NLU.

        It receives the utterance and matches it to the patterns created. If
        required, CheckUserIntents calls annotators to check which slot user
        refers to.

        Args:
            config: Dictionary with domain knowledge and database.
        """
        self.domain: MovieDomain = config["domain"]
        self.database: DataBase = config["database"]
        # Load the preprocessing elements and the Database as slot-values
        self._punctuation_remover()
        self.lemmatizer = WordNetLemmatizer()
        self.data_loader = DataLoader(config, self._lemmatize_value)
        self.slot_values = self.data_loader.load_slot_value_pairs()
        # load the tag-words from the DB
        tag_words_slots = self.data_loader.load_tag_words(
            config["tag_words_slots_path"]
        )
        self.tag_words_user_reveal = tag_words_slots["user_reveal"]
        self.tag_words_user_inquire = tag_words_slots["user_inquire"]
        self.tag_words_user_reveal_inquire = tag_words_slots[
            "user_reveal_inquire"
        ]
        # Load the components for intent detection
        self.slot_annotator = RBAnnotator(
            self._process_utterance, self._lemmatize_value, self.slot_values
        )
        self._lemmatize_value("temp")

    def _punctuation_remover(self, remove_ques: bool = True) -> None:
        """Defines a patterns of punctuation marks to remove/keep in the
        utterance.

        TODO (Ivica Kostric) This should be removed. Move all preprocessing
        operations to moviebot.nlu.text_processing.Tokenizer

        Args:
            remove_ques: Defaults to True.
        """
        punctuation = string.punctuation  # .replace('-', '')
        if not remove_ques:
            punctuation = punctuation.replace("?", "")
        self.punctuation_remover = str.maketrans(
            punctuation, " " * len(punctuation)
        )

    def _process_utterance(self, value, last_sys_act=None) -> str:
        """Preprocesses the user input to get a raw sentence.

        TODO (Ivica Kostric) This should be removed. Move all preprocessing
        operations to moviebot.nlu.text_processing.Tokenizer

        Args:
            value: A string containing user input or values.
            last_sys_act: The previous DAct by the Conversational Agent.
              Defaults to None.

        Returns:
            String having the processed utterance.
        """
        value = value.rstrip().lower()
        value = value.replace("'", "")
        value = value.translate(self.punctuation_remover)
        value = " " + value + " "
        return value

    def _lemmatize_value(self, value, skip_number=False) -> str:
        """Returns lemmatized text.

        TODO (Ivica Kostric) This should be removed. Move all preprocessing
        operations to moviebot.nlu.text_processing.Tokenizer.

        Args:
            value: Value to lemmatize.
            skip_number: Defaults to False.
        """
        value = self._process_utterance(value)
        return " ".join(
            [self.lemmatizer.lemmatize(word) for word in word_tokenize(value)]
        )

    def is_dontcare(self, user_utterance: UserUtterance) -> bool:
        """Returns true if any keyword from dont care pattern is present.

        TODO (Ivica Kostric): This can be partially merged with
        check_basic_intent. Regex can be dropped since we are only looking for
        complete tokens anyway.

        Args:
            utterance: A processed user utterance.

        Returns:
            True if the dont care pattern detected.
        """
        for token in user_utterance.get_tokens():
            for pattern in PATTERN_DONT_CARE:
                match = re.search(r"\b{0}\b".format(pattern), token.lemma)
                if match:
                    return True
        return False

    def _is_question(self, utterance: str) -> bool:
        """Returns true if any keyword from question pattern is present.

        Args:
            utterance: Raw text.

        Returns:
            True if the text is a question.
        """
        if utterance.lower().split()[
            0
        ] in PATTERN_QUESTION or utterance.strip().endswith("?"):
            return True
        else:
            return False

    def check_basic_intent(
        self, user_utterance: UserUtterance, intent: UserIntents
    ) -> List[DialogueAct]:
        """Given intent and a list of intent patterns checks if any token in
        user utterance match the pattern.

        Args:
            user_utterance: Class containing raw utterance and processed tokens.
            intent: Intent for which to compare patterns.

        Returns:
            If pattern exists returns that intents dialogue act.
        """
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        for token in user_utterance.get_tokens():
            if any(
                [
                    re.search(r"\b{0}\b".format(pattern), token.lemma)
                    for pattern in PATTERN_BASIC.get(intent, [])
                ]
            ):
                dact.intent = intent
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def check_reveal_voluntary_intent(
        self, user_utterance: UserUtterance
    ) -> List[DialogueAct]:
        """Finds any voluntary revealed information in utterance.

        Args:
            utterance: Processed user utterance.

        Returns:
            A list of dialogue acts with revealed information.
        """
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        person_name_checks = False
        for slot in self.domain.slots_annotation:
            if slot in [x.value for x in [Slots.ACTORS, Slots.DIRECTORS]]:
                if person_name_checks:
                    continue
                else:
                    person_name_checks = True
            # if slot == Slots.TITLE.value and dact.intent!= UserIntents.UNK:
            # continue
            params = self.slot_annotator.slot_annotation(slot, user_utterance)
            if params:
                dact.intent = UserIntents.REVEAL
                dact.params.extend(params)
                # user_dacts.append(dact)
                # return user_dacts
        if dact.intent != UserIntents.UNK:
            # print(f'All Dacts\n{dact}')
            self._filter_dact(dact, user_utterance.text)
            # print(f'Filtered Dacts\n{dact}')
            if len(dact.params) > 0:
                user_dacts.append(dact)
        return user_dacts

    def check_reveal_intent(
        self, user_utterance, last_agent_dact
    ) -> List[DialogueAct]:
        """Checks utterance for intent "reveal".

        This function is only called if the intent of agent is ELicit to see
        if user has answered the query.

        Args:
            utterance: Processed user utterance.
            last_agent_dact: Last agent dialogue act.

        Returns:
            A list of dialogue acts.
        """
        user_dacts = []
        for param in last_agent_dact.params:
            dact = DialogueAct(UserIntents.UNK, [])
            slot = param.slot
            params = self.slot_annotator.slot_annotation(slot, user_utterance)
            if params:
                dact.intent = UserIntents.REVEAL
                dact.params.extend(params)
            if dact.intent == UserIntents.UNK and self.is_dontcare(
                user_utterance
            ):
                dact.intent = UserIntents.REVEAL
                dact.params.append(
                    ItemConstraint(param.slot, Operator.EQ, Values.DONT_CARE)
                )
            if dact.intent != UserIntents.UNK:
                # print(f'All Dacts\n{dact}')
                self._filter_dact(dact, user_utterance.text)
                # print(f'Filtered Dacts\n{dact}')
                if len(dact.params) > 0:
                    user_dacts.append(dact)
            else:
                dact.intent = UserIntents.REVEAL
                dact.params.append(
                    ItemConstraint(param.slot, Operator.EQ, Values.NOT_FOUND)
                )
                user_dacts.append(dact)
        return user_dacts

    def check_reject_intent(
        self, user_utterance: UserUtterance
    ) -> List[DialogueAct]:
        """Checks utterance for intent "reject".

        Args:
            utterance: Processed user utterance.

        Returns:
            A list of dialogue acts.
        """
        # checking for intent = 'reject'
        tokens = user_utterance.get_tokens()
        utterance = sum(tokens).lemma if tokens else ""
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        if any(
            [
                re.search(r"\b{0}\b".format(pattern), utterance)
                for pattern in PATTERN_DONT_LIKE
            ]
        ):
            dact.intent = UserIntents.REJECT
            preference = convert_choice_to_preference(
                RecommendationChoices.DONT_LIKE
            )
            # TODO: Use enum for constraints' slot.
            # See: https://github.com/iai-group/MovieBot/issues/225
            dact.params = [
                ItemConstraint("reason", Operator.EQ, "dont_like"),
                ItemConstraint("preference", Operator.EQ, preference),
            ]
        elif any(
            [
                re.search(r"\b{0}\b".format(pattern), utterance)
                for pattern in PATTERN_WATCHED
            ]
        ):
            dact.intent = UserIntents.REJECT
            preference = convert_choice_to_preference(
                RecommendationChoices.WATCHED
            )
            dact.params = [
                ItemConstraint("reason", Operator.EQ, "watched"),
                ItemConstraint("preference", Operator.EQ, preference),
            ]
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def check_inquire_intent(
        self, user_utterance: UserUtterance
    ) -> List[DialogueAct]:
        """Checks utterance for intent "inquire".

        Args:
            utterance: Processed user utterance.

        Returns:
            A list of dialogue acts.
        """
        # matching intents to 'list', 'Summarize', 'Subset', 'Compare' and
        # 'Similar'
        tokens = user_utterance.get_tokens()
        utterance = sum(tokens).lemma if tokens else ""
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        for slot, values in self.tag_words_user_inquire.items():
            if any([value for value in values if value in utterance]):
                dact.intent = UserIntents.INQUIRE
                dact.params.append(ItemConstraint(slot, Operator.EQ, ""))
        if (
            dact.intent == UserIntents.UNK
        ):  # and self._is_question(raw_utterance):
            for slot, values in self.tag_words_user_reveal_inquire.items():
                if any([value for value in values if value in utterance]):
                    dact.intent = UserIntents.INQUIRE
                    dact.params.append(ItemConstraint(slot, Operator.EQ, ""))
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def _filter_dact(  # noqa: C901
        self, dact: DialogueAct, raw_utterance: str
    ) -> None:
        """Filters and removes dialogue act parameters if one is a sub-string
        of another.

        More filters are applied to remove the params or
        change slots in a specified sequence if these qualify specific
        conditions.

        Args:
            dact: Dialogue act to filter.
            raw_utterance: Raw user utterance.
        """
        slot_filter_priority = [
            Slots.GENRES,
            Slots.ACTORS,
            Slots.DIRECTORS,
            Slots.KEYWORDS,
            Slots.TITLE,
        ]
        # first see if multiple genres lead to a plot keyword or title
        for slot in slot_filter_priority:
            params = [p for p in dact.params if p.slot == slot.value]
            for param in params:
                if any(
                    [
                        re.search(r"\b{0}\b".format(pattern), param.value)
                        for pattern in PATTERN_DONT_CARE
                        + PATTERN_BASIC[UserIntents.ACKNOWLEDGE]
                        + PATTERN_BASIC[UserIntents.DENY]
                    ]
                ):
                    dact.remove_constraint(param)
                    continue
                if param.slot == Slots.KEYWORDS.value:
                    # remove the plot_keyword if it is also in other slot
                    # values or is a sub-string
                    if param.value in [
                        p.value for p in dact.params if p.slot != param.slot
                    ]:
                        dact.remove_constraint(param)
                if param.slot in [
                    Slots.GENRES.value,
                    Slots.KEYWORDS.value,
                    Slots.ACTORS.value,
                    Slots.DIRECTORS.value,
                ]:
                    # remove genre if it is a sub-string of any other value
                    values = (
                        param.value.strip().split()
                        if param.slot == Slots.GENRES.value
                        else [param.value]
                    )
                    for value in values:
                        for p in dact.params:
                            if (
                                p.slot != param.slot
                                and value in p.value.split()
                                and len(p.value.split()) != len(value.split())
                            ):
                                dact.remove_constraint(param)
                if param.slot == Slots.TITLE.value:
                    # remove the title if it is also in other slot values
                    if param.value in [
                        p.value for p in dact.params if p.slot != param.slot
                    ]:
                        dact.remove_constraint(param)
                    elif param.value in self.slot_values[Slots.KEYWORDS.value]:
                        param.slot = Slots.KEYWORDS.value
                    elif len(
                        [
                            p
                            for p in param.value.split()
                            if p in self.slot_values[Slots.GENRES.value]
                            or p in self.slot_annotator.genres_alternatives
                        ]
                    ) == len(param.value.split()):
                        param.slot = Slots.GENRES.value

        # extra check for if an annotation is a sub-string of another
        for param in dact.params:
            if param.slot in [Slots.YEAR.value, Slots.GENRES.value]:
                continue
            param.value = self.slot_annotator.find_in_raw_utterance(
                raw_utterance, param.value, len(word_tokenize(param.value))
            )
        for param in deepcopy(dact.params):
            if any(
                [
                    param.value.lower() in p.value.lower()
                    and param.value.lower() != p.value.lower()
                    for p in dact.params
                    if p.slot != param.slot
                ]
            ):
                dact.remove_constraint(param)

        self._filter_genres(dact)
        dual_persons = self._filter_person_names(dact)
        values_neg = self._get_annotation_relevance(
            dact, raw_utterance, dual_persons
        )
        for param in dact.params:
            if param.value in values_neg:
                if param.op == Operator.EQ:
                    param.op = Operator.NE
                else:
                    param.value = f"{param.op} {param.value}"
                    param.op = Operator.NE

    def _filter_genres(self, dact: DialogueAct) -> None:
        """Splits genre constraint into sub-constraints.

        Args:
            dact: Dialogue act.
        """
        for param in dact.params:
            values = []
            if param.slot == Slots.GENRES.value:
                values = param.value.split()
                param.value = (
                    values[0]
                    if values[0] in self.slot_values[Slots.GENRES.value]
                    else self.slot_annotator.genres_alternatives[values[0]]
                )
            if len(values) > 1:
                for value in values[1:]:
                    if value not in [
                        p.value for p in dact.params if p.slot == param.slot
                    ]:
                        if value not in self.slot_values[Slots.GENRES.value]:
                            value = self.slot_annotator.genres_alternatives[
                                value
                            ]
                        dact.params.append(
                            ItemConstraint(
                                Slots.GENRES.value, Operator.EQ, value
                            )
                        )

    def _filter_person_names(self, dact: DialogueAct) -> List[str]:
        """Returns persons that can be both actors and directors.

        Args:
            dact: Dialogue act.

        Returns:
            A list of persons that are in both actor and director slot.
        """
        # check if both actor and director exist in annotation
        slots = [x.value for x in [Slots.ACTORS, Slots.DIRECTORS]]
        params = [p for p in dact.params if p.slot in slots]
        if len(params) == 1:
            return []
        param_values = {}
        for param in params:
            if param.value in param_values:
                param_values[param.value].append(param.slot)
            else:
                param_values[param.value] = [param.slot]
        dual_values = [x for x, y in param_values.items() if len(y) > 1]
        return dual_values

    def _get_annotation_relevance(
        self, dact: DialogueAct, raw_utterance: str, dual_person: List[str]
    ) -> List[str]:
        """Returns a list of values that are not wanted.

        Args:
            dact: Dialogue act.
            raw_utterance: Raw user utterance.
            dual_person: List of persons that can be both actors and directors.

        Returns:
            List of values that are not wanted.
        """
        # first sequence the params:
        values = sorted([p.value for p in dact.params], key=raw_utterance.find)
        words_pre_req = dict.fromkeys(values)
        next_ind = 0
        for val in words_pre_req:
            end_ind = raw_utterance.find(val)
            pre_req = raw_utterance[next_ind:end_ind]
            words_pre_req[val] = self._process_utterance(pre_req)
            next_ind = end_ind + len(val)
        param_dontwant = []
        for value, pre_req in words_pre_req.items():
            if any(
                [
                    re.search(r"\b{0}\b".format(pattern), pre_req)
                    for pattern in PATTERN_DONT_WANT
                ]
            ):
                param_dontwant.append(value)
        if dual_person and len(dual_person) > 0:
            for value in dual_person:
                if any(
                    [
                        re.search(
                            r"\b{0}\b".format(pattern), words_pre_req[value]
                        )
                        for pattern in self.tag_words_user_reveal_inquire[
                            Slots.DIRECTORS.value
                        ]
                    ]
                ):
                    dact.remove_constraint(
                        ItemConstraint(Slots.ACTORS.value, Operator.EQ, value)
                    )
                elif any(
                    [
                        re.search(
                            r"\b{0}\b".format(pattern), words_pre_req[value]
                        )
                        for pattern in self.tag_words_user_reveal_inquire[
                            Slots.ACTORS.value
                        ]
                    ]
                ):
                    dact.remove_constraint(
                        ItemConstraint(
                            Slots.DIRECTORS.value, Operator.EQ, value
                        )
                    )
        return param_dontwant
