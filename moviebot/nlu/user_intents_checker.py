""" This file contains the main functions for checking the user intents."""

__author__ = "Javeria Habib"

import re
import string
from copy import deepcopy

import wikipedia
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.item_constraint import ItemConstraint
from moviebot.dialogue_manager.operator import Operator
from moviebot.intents.user_intents import UserIntents
from moviebot.nlu.data_loader import DataLoader
from moviebot.nlu.slot_annotator import SlotAnnotator
from moviebot.dialogue_manager.slots import Slots
from moviebot.dialogue_manager.values import Values


class UserIntentsChecker:
    """CheckUserIntents is a class to detect the intents for the class NLU. It receives the
    utterance and matches it to the patterns created. If required, CheckUserIntents calls
    annotators to check which slot user refers to."""

    def __init__(self, config):
        """ Initialize the Intents checker and load database, tag words etc

        :type self.database: DataBase
        :type self.ontology: Ontology
        """
        self.ontology = config['ontology']
        self.database = config['database']
        # Load the preprocessing elements and the Database as slot-values
        self._punctuation_remover()
        self.lemmatizer = WordNetLemmatizer()
        self.data_loader = DataLoader(config, self._lemmatize_value)
        self.slot_values = self.data_loader.load_database()
        # load the tag-words from the DB
        tag_words_slots = self.data_loader.load_tag_words(config['tag_words_slots_path'])
        self.tag_words_user_reveal = tag_words_slots['user_reveal']
        self.tag_words_user_inquire = tag_words_slots['user_inquire']
        self.tag_words_user_reveal_inquire = tag_words_slots['user_reveal_inquire']
        # Load the components for intent detection
        self._intent_patterns()
        self.slot_annotator = SlotAnnotator(self._process_utterance, self._lemmatize_value,
                                            self.slot_values)
        self._lemmatize_value('temp')

    def _punctuation_remover(self, remove_ques=True):
        """Defines a patterns of punctuation marks to remove/keep in the utterance"""
        punctuation = string.punctuation  # .replace('-', '')
        if not remove_ques:
            punctuation = punctuation.replace('?', '')
        self.punctuation_remover = str.maketrans(punctuation, ' ' * len(punctuation))

    def _process_utterance(self, value, last_sys_act=None):
        """Preprocesses the user input to get a raw sentence.

        :param value: a string containing user input or values
        :param last_sys_act: the previous DAct by the Conversational Agent
        :return: string having the processed utterance
        """
        value = value.rstrip().lower()
        value = value.replace("'", "")
        value = value.translate(self.punctuation_remover)
        value = " " + value + " "
        return value

    def _lemmatize_value(self, value, skip_number=False):
        value = self._process_utterance(value)
        return " ".join([self.lemmatizer.lemmatize(word) for word in word_tokenize(value)])

    def _intent_patterns(self):
        """Designing some patterns to understand the utterance better"""
        self.acknowledge_pattern = ["yes", "okay", "fine", "sure"]
        self.hi_pattern = ['hi', 'hello', 'hey', 'howdy']
        self.deny_pattern = ["no", "nope", "nah", "not"]
        self.dont_care_pattern = ["anything", "any", "dont know", "i do not care", "i dont care",
                                  "dont care", "dontcare", "it does not matter",
                                  "it doesnt matter", "does not matter", "doesnt matter",
                                  "no one", "no body", "nobody", "nothing", "none"]
        self.bye_pattern = ["bye", "goodbye", "quit", "exit"]
        # Patterns to check if offer or partial offer is made
        self.question_pattern = ["who", "what", "when", "which", "can", "could", "is", "are"]
        self.dontlike_movie_pattern = ['something else', 'anything else', 'dont like it',
                                       'not this',
                                       'another']
        self.dontwant_pattern = ["dont", "not", "nothing", "wont", 'shouldnt', "dont need",
                                 "dont want", "no", "not"]
        self.watched_pattern = ['watched', 'seen', 'yes', 'I have', 'yup', 'yea']

    def is_dontcare(self, utterance):
        for pattern in self.dont_care_pattern:
            match = re.search(r'\b{0}\b'.format(pattern), utterance)
            if match:
                return True

    def _is_question(self, utterance):
        if utterance.lower().split()[0] in self.question_pattern or utterance.strip().endswith('?'):
            return True
        else:
            return False

    def check_acknowledge_intent(self, utterance):
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        for pattern in self.acknowledge_pattern:
            match = re.search(r'\b{0}\b'.format(pattern), utterance)
            if match:
                dact.intent = UserIntents.ACKNOWLEDGE
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def check_deny_intent(self, utterance):
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        for pattern in self.deny_pattern:
            match = re.search(r'\b{0}\b'.format(pattern), utterance)
            if match:
                dact.intent = UserIntents.DENY
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def check_bye_intent(self, utterance):
        # checking for intent = "bye"
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        if any([re.search(r'\b{0}\b'.format(pattern), utterance) for pattern in
                self.bye_pattern]):
            dact.intent = UserIntents.BYE
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def check_hi_intent(self, utterance):
        """Checking for a starting message"""
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        if any([re.search(r'\b{0}\b'.format(pattern), utterance) for pattern in
                self.hi_pattern]):
            dact.intent = UserIntents.HI
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def check_reveal_voluntary_intent(self, utterance, raw_utterance):
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        person_name_checks = False
        for slot in self.ontology.slots_annotation:
            if slot in [x.value for x in [Slots.ACTORS, Slots.DIRECTORS]]:
                if person_name_checks:
                    continue
                else:
                    person_name_checks = True
            # if slot == Slots.TITLE.value and dact.intent!= UserIntents.UNK: continue
            params = self.slot_annotator.slot_annotation(slot, utterance, raw_utterance)
            if params:
                dact.intent = UserIntents.REVEAL
                dact.params.extend(params)
                # user_dacts.append(dact)
                # return user_dacts
        if dact.intent != UserIntents.UNK:
            # print(f'All Dacts\n{dact}')
            self._filter_dact(dact, raw_utterance)
            # print(f'Filtered Dacts\n{dact}')
            if len(dact.params) > 0:
                user_dacts.append(dact)
        return user_dacts

    def check_reveal_intent(self, utterance, raw_utterance, last_agent_dact):
        """This function is only called if the intent of agent is ELicit to see if user has
        answered the query"""
        user_dacts = []
        for param in last_agent_dact.params:
            dact = DialogueAct(UserIntents.UNK, [])
            slot = param.slot
            params = self.slot_annotator.slot_annotation(slot, utterance, raw_utterance)
            if params:
                dact.intent = UserIntents.REVEAL
                dact.params.extend(params)
            if dact.intent == UserIntents.UNK and self.is_dontcare(utterance):
                dact.intent = UserIntents.REVEAL
                dact.params.append(ItemConstraint(param.slot, Operator.EQ, Values.DONT_CARE))
            if dact.intent != UserIntents.UNK:
                # print(f'All Dacts\n{dact}')
                self._filter_dact(dact, raw_utterance)
                # print(f'Filtered Dacts\n{dact}')
                if len(dact.params) > 0:
                    user_dacts.append(dact)
            else:
                dact.intent = UserIntents.REVEAL
                dact.params.append(ItemConstraint(param.slot, Operator.EQ, Values.NOT_FOUND))
                user_dacts.append(dact)
        return user_dacts

    def check_reject_intent(self, utterance):
        # checking for intent = "reject"
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        if any([re.search(r'\b{0}\b'.format(pattern), utterance) for pattern in
                self.dontlike_movie_pattern]):
            dact.intent = UserIntents.REJECT
            dact.params = [ItemConstraint('reason', Operator.EQ, 'dont_like')]
        elif any([re.search(r'\b{0}\b'.format(pattern), utterance) for pattern in
                  self.watched_pattern]):
            dact.intent = UserIntents.REJECT
            dact.params = [ItemConstraint('reason', Operator.EQ, 'watched')]
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def check_inquire_intent(self, utterance):
        # matching intents to "list", "Summarize", "Subset", "Compare" and "Similar"
        user_dacts = []
        dact = DialogueAct(UserIntents.UNK, [])
        for slot, values in self.tag_words_user_inquire.items():
            if any([value for value in values if value in utterance]):
                dact.intent = UserIntents.INQUIRE
                dact.params.append(ItemConstraint(slot, Operator.EQ, ""))
        if dact.intent == UserIntents.UNK:  # and self._is_question(raw_utterance):
            for slot, values in self.tag_words_user_reveal_inquire.items():
                if any([value for value in values if value in utterance]):
                    dact.intent = UserIntents.INQUIRE
                    dact.params.append(ItemConstraint(slot, Operator.EQ, ""))
        if dact.intent != UserIntents.UNK:
            user_dacts.append(dact)
        return user_dacts

    def generate_params_continue_recommendation(self, item_in_focus):
        movie_title = item_in_focus[Slots.TITLE.value]
        results = wikipedia.search(f'I need a film similar to {movie_title}', 20)
        results = [r.split('(')[0].strip() for r in results]
        for result in deepcopy(results):
            if result not in self.slot_values[Slots.TITLE.value]:
                results.remove(result)
        if len(results) > 0:
            return [ItemConstraint(Slots.TITLE.value, Operator.EQ, str(results))]
        else:
            results = wikipedia.search(f'I need a movie similar to {movie_title}', 20)
            results = [r.split('(')[0].strip() for r in results]
            for result in deepcopy(results):
                if result not in self.slot_values[Slots.TITLE.value]:
                    results.remove(result)
            if len(results) > 0:
                return [ItemConstraint(Slots.TITLE.value, Operator.EQ, str(results))]

    def _remove_param(self, param, dact):
        for p in dact.params:
            if p.slot == param.slot and p.value == param.value:
                dact.params.remove(p)
                return

    def _filter_dact(self, dact, raw_utterance):
        """ This algortihm filters the DActs parameters and remove if one is a sub-string of
        another.
        More filters are applied to remove the params or change slots in a specified sequence if
        these qualify
        specific conditions"""
        slot_filter_priority = [Slots.GENRES, Slots.ACTORS, Slots.DIRECTORS,
                                Slots.KEYWORDS, Slots.TITLE]
        # first see if multiple genres lead to a plot keyword or title
        for slot in slot_filter_priority:
            params = [p for p in dact.params if p.slot == slot.value]
            for param in params:
                if any([re.search(r'\b{0}\b'.format(pattern), param.value) for pattern in
                        self.dont_care_pattern + self.acknowledge_pattern + self.deny_pattern]):
                    self._remove_param(param, dact)
                    continue
                if param.slot == Slots.KEYWORDS.value:
                    # remove the plot_keyword if it is also in other slot values or is a sub-string
                    if param.value in [p.value for p in dact.params if p.slot != param.slot]:
                        self._remove_param(param, dact)
                if param.slot in [Slots.GENRES.value, Slots.KEYWORDS.value,
                                  Slots.ACTORS.value, Slots.DIRECTORS.value]:
                    # remove genre if it is a sub-string of any other value
                    values = param.value.strip().split() if param.slot == Slots.GENRES.value \
                        else [param.value]
                    for value in values:
                        for p in dact.params:
                            if p.slot != param.slot and value in p.value.split() and \
                                    len(p.value.split()) != len(value.split()):
                                self._remove_param(param, dact)
                if param.slot == Slots.TITLE.value:
                    # remove the title if it is also in other slot values
                    if param.value in [p.value for p in dact.params if p.slot != param.slot]:
                        self._remove_param(param, dact)
                    elif param.value in self.slot_values[Slots.KEYWORDS.value]:
                        param.slot = Slots.KEYWORDS.value
                    elif len([p for p in param.value.split() if p in self.slot_values[
                        Slots.GENRES.value] or p in self.slot_annotator.genres_alternatives]) == \
                            len(param.value.split()):
                        param.slot = Slots.GENRES.value

        # extra check for if an annotation is a sub-string of another
        for param in dact.params:
            if param.slot in [Slots.YEAR.value, Slots.GENRES.value]: continue
            param.value = self.slot_annotator.find_in_raw_utterance(raw_utterance, param.value,
                                                                    len(word_tokenize(param.value)))
        for param in deepcopy(dact.params):
            if any([param.value.lower() in p.value.lower() and param.value.lower() != \
                    p.value.lower() for p in dact.params if p.slot != param.slot]):
                self._remove_param(param, dact)

        self._filter_genres(dact)
        dual_persons = self._filter_person_names(dact)
        values_neg = self._get_annotation_relevance(dact, raw_utterance, dual_persons)
        for param in dact.params:
            if param.value in values_neg:
                if param.op == Operator.EQ:
                    param.op = Operator.NE
                else:
                    param.value = f'{param.op} {param.value}'
                    param.op = Operator.NE

    def _filter_genres(self, dact):
        for param in dact.params:
            values = []
            if param.slot == Slots.GENRES.value:
                values = param.value.split()
                param.value = values[0] if values[0] in self.slot_values[Slots.GENRES.value] else \
                    self.slot_annotator.genres_alternatives[values[0]]
            if len(values) > 1:
                for value in values[1:]:
                    if value not in [p.value for p in dact.params if p.slot == param.slot]:
                        if value not in self.slot_values[Slots.GENRES.value]:
                            value = self.slot_annotator.genres_alternatives[value]
                        dact.params.append(ItemConstraint(Slots.GENRES.value, Operator.EQ, value))

    def _filter_person_names(self, dact):
        # check if both actor and director exist in annotation
        slots = [x.value for x in [Slots.ACTORS, Slots.DIRECTORS]]
        params = [p for p in dact.params if p.slot in slots]
        if len(params) == 1: return []
        param_values = {}
        for param in params:
            if param.value in param_values:
                param_values[param.value].append(param.slot)
            else:
                param_values[param.value] = [param.slot]
        dual_values = [x for x, y in param_values.items() if len(y) > 1]
        return dual_values

    def _get_annotation_relevance(self, dact, raw_utterance, dual_person):
        """
        Get the relevance if user really want a preference or wants to remove it from the list
        """
        words_seq = word_tokenize(raw_utterance)
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
            if any([re.search(r'\b{0}\b'.format(pattern), pre_req) for pattern in
                    self.dontwant_pattern]):
                param_dontwant.append(value)
        if dual_person and len(dual_person) > 0:
            for value in dual_person:
                if any([re.search(r'\b{0}\b'.format(pattern), words_pre_req[value]) for pattern in
                        self.tag_words_user_reveal_inquire[Slots.DIRECTORS.value]]):
                    self._remove_param(ItemConstraint(Slots.ACTORS.value, Operator.EQ, value), dact)
                elif any([re.search(r'\b{0}\b'.format(pattern), words_pre_req[value]) for pattern in
                          self.tag_words_user_reveal_inquire[Slots.ACTORS.value]]):
                    self._remove_param(ItemConstraint(Slots.DIRECTORS.value, Operator.EQ, value),
                                       dact)
        return param_dontwant
