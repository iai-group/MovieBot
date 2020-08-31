"""NLG is a Natural Language Generator used to produce a human-like response for Dialogue Acts
of the agent."""

__author__ = "Javeria Habib"

import random
from copy import deepcopy
from typing import List

from iaibot.dialogue_manager.dialogue_act import DialogueAct
from iaibot.dialogue_manager.dialogue_state import DialogueState
from iaibot.dialogue_manager.item_constraint import ItemConstraint
from iaibot.dialogue_manager.operator import Operator
from iaibot.intents.agent_intents import AgentIntents
from iaibot.intents.user_intents import UserIntents
from iaibot.dialogue_manager.slots import Slots
from iaibot.dialogue_manager.values import Values


class NLG:
    """NLG is a Natural Language Generator used to produce a human-like response for Dialogue
    Acts of the agent.
    """

    def __init__(self, args=None):
        """Initializes any necessary components.

        :type self.dialogue_state: DialogueState
        :param args: basic settings of NLG
        """
        self.dialogue_state = None
        self.previous_count = 0
        self.agent_elicit_nlg = {
            Slots.GENRES.value: ["Do you have any specific genres in mind?",
                                 "Which genres do you prefer?"],
            Slots.KEYWORDS.value: ["Can you give me a few keywords?",
                                   "What are you looking for in a movie? Some keywords "
                                   "would be good."],
            Slots.DIRECTORS.value: ["Any specific director you are looking for?",
                                    "Is there any specific director in your mind?"],
            Slots.ACTORS.value: ["Do you have any favourite actor these days?",
                                 "Any hints regarding the cast? Can you give me a name of any "
                                 "actor?"],
            Slots.YEAR.value: ["Which timeline do you prefer? For example, 90s or 80s?",
                               "Do you have any preference of when the movie was produced? "
                               "For example, 1992 or  90s."]
        }

        self.inform_key = {
            Slots.TITLE.value: f'_{Slots.TITLE.value}_',
            Slots.GENRES.value: f'_{Slots.GENRES.value}_',
            Slots.PLOT.value: f'_{Slots.PLOT.value}_',
            Slots.KEYWORDS.value: f'_{Slots.KEYWORDS.value}_',
            Slots.DIRECTORS.value: f'_{Slots.DIRECTORS.value}_',
            Slots.DURATION.value: f'_{Slots.DURATION.value}_',
            Slots.ACTORS.value: f'_{Slots.ACTORS.value}_',
            Slots.YEAR.value: f'_{Slots.YEAR.value}_',
            Slots.MOVIE_LINK.value: f'_{Slots.MOVIE_LINK.value}_',
            Slots.RATING.value: f'_{Slots.RATING.value}_'
        }

        self.agent_inform_nlg = {
            Slots.TITLE.value: [
                f'The title of the movie is "{self.inform_key[Slots.TITLE.value]}".',
                f'Its name is "{self.inform_key[Slots.TITLE.value]}".'
            ],
            Slots.GENRES.value: [
                f'The genres it belongs to are {self.inform_key[Slots.GENRES.value]}.',
                f'Its genres are {self.inform_key[Slots.GENRES.value]}.'
            ],
            Slots.PLOT.value: [
                f'{self.inform_key[Slots.PLOT.value]}'
            ],
            Slots.KEYWORDS.value: [
                f'The plot of the movie revolves around {self.inform_key[Slots.KEYWORDS.value]}.',
                f'The movie plot is about {self.inform_key[Slots.KEYWORDS.value]}.'
            ],
            Slots.DIRECTORS.value: [
                f'The director of this movie is {self.inform_key[Slots.DIRECTORS.value]}.',
                f'Its directed by {self.inform_key[Slots.DIRECTORS.value]}.'
            ],
            Slots.DURATION.value: [
                f'Its duration is {self.inform_key[Slots.DURATION.value]}.',
                f'This movie is {self.inform_key[Slots.DURATION.value]} long.'
            ],
            Slots.ACTORS.value: [
                f'Some of the famous actors in this movie are '
                f'{self.inform_key[Slots.ACTORS.value]}.',
                f'Actors {self.inform_key[Slots.ACTORS.value]} have played prominent roles in '
                f'this movie.'
            ],
            Slots.YEAR.value: [
                f'The movie was released in {self.inform_key[Slots.YEAR.value]}.',
                f'It was released in the year {self.inform_key[Slots.YEAR.value]}.'
            ],
            Slots.MOVIE_LINK.value: [
                f'The link of the movie on IMDb is {self.inform_key[Slots.MOVIE_LINK.value]}',
                f'You can find more about the movie at this link: '
                f'{self.inform_key[Slots.MOVIE_LINK.value]}'
            ],
            Slots.RATING.value: [
                f'Its rating on IMDb is {self.inform_key[Slots.RATING.value]}.',
                f'The rating of this movie on IMDb is {self.inform_key[Slots.RATING.value]}.'
            ]
        }

        self.slot_not_found_gen = {
            Slots.GENRES.value: ["I could not find the genres you mentioned."],
            Slots.KEYWORDS.value: ["I couldn't find the keywords in your response."],
            Slots.DIRECTORS.value: ["I could not find the the director name you specified."],
            Slots.ACTORS.value: ["I couldn't find the The actor you mentioned."],
            Slots.YEAR.value: ["I couldn't find any timeline specification."]
        }

        self.slot_not_found = {
            Slots.GENRES.value: ["I could not find the genres __replace__."],
            Slots.KEYWORDS.value: ["I couldn't find the keywords __replace__."],
            Slots.DIRECTORS.value: ["I could not find the the director name __replace__."],
            Slots.ACTORS.value: ["I couldn't find the The actor __replace__."],
            Slots.YEAR.value: ["I couldn't find any timeline specification."]
        }

    def generate_output(self, agent_dacts, dialogue_state=None, user_fname=None):
        """Selects an appropriate response based on the dialogue acts.

        :type agent_dacts: List[DialogueAct]
        :type dialogue_state: DialogueState
        :param agent_dacts: a list of agent dialogue acts
        :param dialogue_state: the current dialogue state
        :return: string containing natural response
        """
        if dialogue_state:
            CIN = deepcopy(dialogue_state.frame_CIN)
            self.dialogue_state = dialogue_state
        utterance = []
        user_options = {}

        if dialogue_state and dialogue_state.last_user_dacts:
            for user_dact in dialogue_state.last_user_dacts:
                if user_dact.intent == UserIntents.REVEAL:
                    for param in user_dact.params:
                        if param.value == Values.NOT_FOUND:
                            if len(dialogue_state.user_utterance.split()) <= 3:
                                not_found_response = random.choice(self.slot_not_found[param.slot])
                                utterance.append(not_found_response.replace('__replace__',
                                                                            dialogue_state.user_utterance))
                            else:
                                utterance.append(random.choice(self.slot_not_found_gen[param.slot]))
                        elif param.value != Values.DONT_CARE:
                            pass
        for agent_dact in agent_dacts:
            if agent_dact.intent == AgentIntents.WELCOME:
                isBot = False
                new_user = False
                intent_response = ""
                for param in agent_dact.params:
                    if param.slot == 'new_user': new_user = param.value
                    if param.slot == 'is_bot': isBot = param.value
                if isBot:
                    if new_user:
                        intent_response += f'Hi {user_fname}. Welcome to IAI MovieBot. '
                    else:
                        intent_response += f'Hi {user_fname}. Welcome back. '
                welcome_message = ['How may I help you?', 'How can I assist you today?',
                                   'Shall we start?']
                if len(agent_dacts) == 1: intent_response += f'{random.choice(welcome_message)}'
                utterance.append(intent_response)
            if agent_dact.intent == AgentIntents.RESTART:
                utterance.append(random.choice(['Let\'s restart.', 'We are starting again.']))
            elif agent_dact.intent == AgentIntents.ELICIT:
                intent_response = random.choice(self.agent_elicit_nlg[agent_dact.params[0].slot])
                if agent_dact.params[0].value:
                    intent_response += f' For example, {agent_dact.params[0].value}.'
                utterance.append(intent_response)
            elif agent_dact.intent == AgentIntents.COUNT_RESULTS:
                for param in agent_dact.params:
                    if param.slot == 'count':
                        round_value = int(round(param.value / 100.0)) * 100
                        clarify_response = self._clarify_CIN(CIN, agent_dact)
                        if len(clarify_response.split()) == 1:
                            narrow_space = ['Can you guide me to narrow down the search space?',
                                            'Please answer a few questions to help me find a good '
                                            'movie.']
                            intent_response = random.choice(narrow_space)
                        else:
                            count_message = [f'There are almost {round_value} {clarify_response}.',
                                             f'I have found almost {round_value} {clarify_response}.']
                            narrow_space = [
                                'Can you guide me more to narrow down the search space?',
                                'Please answer a few more questions to help me find a '
                                'good movie.']
                            intent_response = " ".join([random.choice(count_message),
                                                        random.choice(narrow_space)])
                        if round_value != self.previous_count:
                            utterance.append(intent_response)
                            self.previous_count = round_value
                        if dialogue_state.agent_must_clarify:
                            user_options.update(self._user_options_remove_preference(deepcopy(
                                dialogue_state.dual_params)))
            elif agent_dact.intent == AgentIntents.RECOMMEND:
                for param in agent_dact.params:
                    if param.slot == Slots.TITLE.value:
                        clarify_response = self._clarify_CIN(CIN, agent_dact)
                        clarify_response = 'an ' + clarify_response if clarify_response[0] in [
                            'a', 'e', 'i', 'o', 'u'] else 'a ' + clarify_response
                        link = dialogue_state.item_in_focus[Slots.MOVIE_LINK.value]
                        clarify_response = [f'I would like to recommend you {clarify_response} '
                                            f'named **"[{param.value}]({link})"**. Have '
                                            f'you watched it?',
                                            f'There is {clarify_response} named '
                                            f'**"[{param.value}]({link})"**. '
                                            f'Have you seen this one?']
                        intent_response = random.choice(clarify_response)
                        # if dialogue_state.agent_repeats_offer:
                        #     intent_response = "(This has been recommended before but I am out " \
                        #                       "of options. Sorry)\n" + \
                        #                       intent_response
                        utterance.append(intent_response)
                        user_options.update(self._user_options_recommend())
                        if dialogue_state.agent_must_clarify:
                            user_options.update(self._user_options_remove_preference(deepcopy(
                                dialogue_state.dual_params)))
            elif agent_dact.intent == AgentIntents.NO_RESULTS:
                intent_response = random.choice(
                    [f'Sorry, I don\'t have any '
                     f'{"other " if dialogue_state.items_in_context else ""}'
                     f'{self._clarify_CIN(CIN, agent_dact)}.',
                     f'Sorry, I couldn\'t find any '
                     f'{"other " if dialogue_state.items_in_context else ""}'
                     f'{self._clarify_CIN(CIN, agent_dact)}.'])
                intent_response += ' Please select from the list of options to continue.'
                utterance.append(intent_response)
                if dialogue_state.agent_must_clarify:
                    user_options.update(self._user_options_remove_preference(deepcopy(
                        dialogue_state.dual_params)))
                else:
                    user_options.update(self._user_options_remove_preference_CIN(CIN))
            elif agent_dact.intent == AgentIntents.INFORM:
                for param in deepcopy(agent_dact.params):
                    if param.slot == Slots.MORE_INFO.value:
                        intent_response = random.choice([f'What would you like to know '
                                                         f'about '
                                                         f'"{param.value}"?'])
                    elif param.slot == 'deny':
                        intent_response = random.choice([f'Would you want to know more about '
                                                         f'"{param.value}"?'])
                    else:
                        intent_response = random.choice(self.agent_inform_nlg[param.slot])
                        if param.value:
                            if param.slot == Slots.DURATION.value:
                                param.value = self._summarize_duration(param.value)
                            intent_response = intent_response.replace(self.inform_key[param.slot],
                                                                      str(param.value))
                            # if param.slot == Slots.PLOT.value:
                            #     intent_response += 'You can see more '
                        else:
                            intent_response = intent_response.replace(self.inform_key[param.slot],
                                                                      'unknown')
                    user_options.update(self._user_options_inquire(dialogue_state))
                    utterance.append(intent_response)
            elif agent_dact.intent == AgentIntents.CONTINUE_RECOMMENDATION:
                utterance.append('Please choose your next step:')
                user_options.update(self._user_options_continue(agent_dact))
            elif agent_dact.intent == AgentIntents.BYE:
                bye_message = ['I hope you had a good experience. Bye.',
                               'Hope to see you soon. Bye.']
                utterance.append(random.choice(bye_message))
            elif agent_dact.intent == AgentIntents.CANT_HELP:
                cant_help_message = ['Sorry I can\'t help you with that.',
                                     'I believe I am stuck. I can\'t help you here.']
                utterance.append(random.choice(cant_help_message))
        if len(utterance) == 0:
            return " ".join([str(dact) for dact in agent_dacts]), user_options
        return '\n\n'.join(utterance), user_options

    def _summarize_duration(self, value):
        value = int(value)
        hours = int(value / 60)
        minutes = value - int(value / 60) * 60
        if minutes > 60:
            return random.choice([f'{value} minutes',
                                  f'{hours} {"hours" if hours > 1 else "hour"} and '
                                  f'{minutes} {"minutes" if minutes > 1 else "minute"}'])
        else:
            return f'{value} minutes'

    def _summarize_title_year(self, value):
        """ :type value: str
        """
        negate = False
        if value.startswith('.NOT.'):
            negate = True
            value = value.replace('.NOT.', '')
        if value.strip().startswith('BETWEEN'):
            years = [int(x) for x in value.split() if str.isdigit(x)]
            difference = years[1] - years[0]
            if difference == 10:
                return str(years[0])[-2:] + 's'
            elif difference == 100:
                return str(years[0])[:1] + 'th century'
        else:
            return f'year {"not " if negate else " "}' + value

    def _clarify_CIN(self, CIN, agent_dact):
        """Clarify the user CIN in the utterance

        :param CIN: current information need
        :param agent_dact: agent dialogue act
        :return: a string for system utterance
        """
        if self.dialogue_state.agent_should_offer_similar:
            response = f' film similar to "{list(self.dialogue_state.similar_movies.keys())[0]}" '
            return response
        response = ""
        negate = '.NOT.'
        genres_list = []
        if CIN[Slots.GENRES.value]:
            genres_list = [x for x in CIN[Slots.GENRES.value] if x not in Values.__dict__.values()]
            for genre in deepcopy(genres_list):
                if genre.startswith(negate):
                    genres_list.remove(genre)
                    genres_list.append(f'non {genre.replace(negate, "")}')
            genres = ''
            if len(genres_list) > 0:
                genres = ', '.join(genres_list[:-1]) + ' and ' + genres_list[-1] if len(
                    genres_list) > 1 else genres_list[-1]
            if genres: response = response + ' ' + genres
        if CIN[Slots.KEYWORDS.value] and CIN[Slots.KEYWORDS.value] not in Values.__dict__.values():
            CIN[Slots.KEYWORDS.value] = CIN[Slots.KEYWORDS.value].replace(negate, 'non ')
            if CIN[Slots.KEYWORDS.value] not in genres_list:
                response = response + ', ' + CIN[Slots.KEYWORDS.value] if response else \
                    CIN[Slots.KEYWORDS.value]
        response = response + ' film' if agent_dact.intent == AgentIntents.RECOMMEND else response \
                                                                                          + ' films'
        if CIN[Slots.TITLE.value]:
            if not (agent_dact.intent == AgentIntents.RECOMMEND and agent_dact.params[0].slot ==
                    Slots.TITLE.value and agent_dact.params[0].value.lower() == CIN[
                        Slots.TITLE.value].lower()):
                if CIN[Slots.TITLE.value].startswith('.NOT.'):
                    response = response + ' named not similar to ' + CIN[Slots.TITLE.value].replace(
                        negate, '')
                else:
                    response = response + ' named similar to ' + CIN[Slots.TITLE.value]
        if CIN[Slots.DIRECTORS.value] and CIN[
            Slots.DIRECTORS.value] not in Values.__dict__.values():
            if CIN[Slots.DIRECTORS.value].startswith('.NOT.'):
                response = response + ' not directed by ' + CIN[Slots.DIRECTORS.value].replace(
                    negate, '')
            else:
                response = response + ' directed by ' + CIN[Slots.DIRECTORS.value]
        if CIN[Slots.YEAR.value] and CIN[Slots.YEAR.value] not in Values.__dict__.values():
            response = response + ' from the ' + self._summarize_title_year(CIN[Slots.YEAR.value])
        if CIN[Slots.ACTORS.value] and CIN[Slots.ACTORS.value] not in Values.__dict__.values():
            if CIN[Slots.ACTORS.value].startswith('.NOT.'):
                response = response + ' not starring ' + CIN[Slots.ACTORS.value].replace(
                    negate, '')
            else:
                response = response + ' starring ' + CIN[Slots.ACTORS.value].title()
        return response.strip()

    def _user_options_continue(self, agent_dact):
        """Give user options to continue when needed"""
        if agent_dact.intent == AgentIntents.CONTINUE_RECOMMENDATION:
            options = {
                DialogueAct(UserIntents.CONTINUE_RECOMMENDATION, []):
                    ["I would like a similar recommendation."],
                DialogueAct(UserIntents.RESTART, []):
                    ['I want to restart for a new movie.'],
                DialogueAct(UserIntents.BYE, []):
                    ['I would like to quit now.']
            }
            return options

    def _user_options_recommend(self):
        """Give use button options when making a recommendation
        :return: a list of button options"""
        options = {
            DialogueAct(UserIntents.REJECT, [ItemConstraint('reason', Operator.EQ, 'watched')]):
                ['I have already watched it.'],
            # [random.choice(['I have already watched it.',
            #                 'I have seen this already.'])],
            DialogueAct(UserIntents.REJECT, [ItemConstraint('reason', Operator.EQ, 'dont_like')]):
                ['Recommend me something else please.'],
            # [random.choice(['I don\'t like this recommendation.',
            #                 'Recommend me something else please.'])],
            DialogueAct(UserIntents.ACCEPT, []): ['I like this recommendation.'],
            DialogueAct(UserIntents.INQUIRE, [ItemConstraint(Slots.MORE_INFO.value, Operator.EQ,
                                                             '')]):
                [random.choice(['Tell me something about it.',
                                'Tell me more about it.'])]
        }
        options.update({'/restart': ['/restart']})
        return options

    def _user_options_remove_preference(self, dual_params):
        """Generate options for user to select in case of two parameters have same value

        :param dual_params: The current parameters with two slots
        :return: a list of button options
        """
        options = {}
        for value, params in dual_params.items():
            for param in params:
                negative = False
                if value.startswith('.NOT.'):
                    negative = True  # TODO. Add changes here
                    value = value.replace('.NOT.', '')
                _a_an = 'an' if value[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
                param_key = DialogueAct(UserIntents.REMOVE_PREFERENCE, [param])
                if param == Slots.GENRES.value:
                    if negative:
                        options[param_key] = [random.choice([f'I want {_a_an} "{value}" '
                                                             f'genre movie.',
                                                             f'I would prefer {_a_an} "{value}" '
                                                             f'genre film.'])]
                    else:
                        options[param_key] = [random.choice([f'Don\'t want {_a_an} "{value}" genre'
                                                             f'movie.',
                                                             f'Won\'t prefer {_a_an} "{value}" '
                                                             f'genre film.'])]
                elif param == Slots.TITLE.value:
                    if negative:
                        options[param_key] = [f'I want movies named like "{value}".']
                    else:
                        options[param_key] = [f'No movies named like "{value}".']
                elif param == Slots.KEYWORDS.value:
                    if negative:
                        options[param_key] = [f'I need movies based on "{value}".']
                    else:
                        options[param_key] = [random.choice([f'Don\'t need movies based on '
                                                             f'"{value}".',
                                                             f'No need of {_a_an} "{value}" film.'])]
                elif param == Slots.DIRECTORS.value:
                    if negative:
                        options[param_key] = [
                            random.choice([f'I want the director "{value.title()}".',
                                           f'Should be directed by "{value.title()}".'])]
                    else:
                        options[param_key] = [
                            random.choice([f'Don\'t want the director "{value.title()}".',
                                           f'Shouldn\'t be directed by "{value.title()}".'])]
                elif param == Slots.ACTORS.value:
                    if negative:
                        options[param_key] = [f'I want the actor "{value.title()}".']
                    else:
                        options[param_key] = [
                            random.choice([f'Don\'t consider actor "{value.title()}".',
                                           f'Remove "{value.title()}" from the list of actors.'])]
                elif param == Slots.YEAR.value:
                    if negative:
                        options[param_key] = [random.choice([f'Release year should be the "'
                                                             f'{self._summarize_title_year(value)}".',
                                                             f'Need a movie from the "'
                                                             f'{self._summarize_title_year(value)}".'])]
                    else:
                        options[param_key] = [random.choice([f'Release year shouldn\'t be the "'
                                                             f'{self._summarize_title_year(value)}".',
                                                             f'Don\'t need a movie from the "'
                                                             f'{self._summarize_title_year(value)}".'])]
                options.update({'/restart': ['/restart']})
        return options

    def _user_options_inquire(self, dialogue_state):
        """

        :type dialogue_state: DialogueState
        :return: list of user requestables as buttons
        """
        options = {}
        requestables = {
            Slots.GENRES.value: 'genres',
            Slots.PLOT.value: 'movie plot',
            Slots.DIRECTORS.value: 'director name',
            Slots.DURATION.value: 'duration',
            Slots.ACTORS.value: 'list of actors',
            Slots.YEAR.value: 'release year',
            Slots.RATING.value: 'rating'
        }
        for slot in dialogue_state.user_requestable:
            dact = DialogueAct(UserIntents.INQUIRE, [ItemConstraint(slot, Operator.EQ, '')])
            options[dact] = requestables.get(slot, 'Invalid slot')
        options.update({
            DialogueAct(UserIntents.REJECT, [ItemConstraint('reason', Operator.EQ, 'dont_like')]):
                ['I don\'t like this recommendation.'],
            # [random.choice(['I don\'t like this recommendation.',
            #                 'Recommend me something else please.'])],
            DialogueAct(UserIntents.ACCEPT, []): ['I like this recommendation.'],
            DialogueAct(UserIntents.CONTINUE_RECOMMENDATION, []):
                ["I would like a similar recommendation."],
            DialogueAct(UserIntents.RESTART, []):
                ['I want to restart for a new movie.'],
        })
        return options

    def _user_options_remove_preference_CIN(self, CIN):
        """Generate options for user to select a parameter to remove

        :type CIN: dict
        :param CIN: The current information needs
        :return: a list of button options
        """
        options = {}
        params = []
        for slot, values in CIN.items():
            if not values: continue
            if isinstance(values, list):
                params.extend([ItemConstraint(slot, Operator.EQ, value) for value in set(values) if
                               value not in Values.__dict__.values() and not value.startswith(
                                   '.NOT.')])
            else:
                if values not in Values.__dict__.values() and not values.startswith('.NOT.'):
                    params.append(ItemConstraint(slot, Operator.EQ, values))

        for param in params:
            value = deepcopy(param.value)
            negative = False
            if value.startswith('.NOT.'):
                negative = True  # TODO. Add changes here
                value = value.replace('.NOT.', '')
            _a_an = 'an' if value[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'
            param_key = DialogueAct(UserIntents.REMOVE_PREFERENCE, [param])
            if param.slot == Slots.GENRES.value:
                if negative:
                    options[param_key] = [random.choice([f'I want {_a_an} "{value}" movie.',
                                                         f'I would prefer {_a_an} "{value}" '
                                                         f'film.'])]
                else:
                    options[param_key] = [random.choice([f'Don\'t want {_a_an} "{value}" '
                                                         f'movie.',
                                                         f'Won\'t prefer {_a_an} "{value}" film.'])]
            elif param.slot == Slots.TITLE.value:
                if negative:
                    options[param_key] = [f'I want movies named like "{value}".']
                else:
                    options[param_key] = [f'No movies named like "{value}".']
            elif param.slot == Slots.KEYWORDS.value:
                if negative:
                    options[param_key] = [f'I need movies based on "{value}".']
                else:
                    options[param_key] = [random.choice([f'Don\'t need movies based on '
                                                         f'"{value}".',
                                                         f'No need of {_a_an} "{value}" film.'])]
            elif param.slot == Slots.DIRECTORS.value:
                if negative:
                    options[param_key] = [
                        random.choice([f'I want the director "{value.title()}".',
                                       f'Should be directed by "{value.title()}".'])]
                else:
                    options[param_key] = [
                        random.choice([f'Don\'t want the director "{value.title()}".',
                                       f'Shouldn\'t be directed by "{value.title()}".'])]
            elif param.slot == Slots.ACTORS.value:
                if negative:
                    options[param_key] = [f'I want the actor "{value.title()}".']
                else:
                    options[param_key] = [
                        random.choice([f'Don\'t consider actor "{value.title()}".',
                                       f'Remove "{value.title()}" from the list of actors.'])]
            elif param.slot == Slots.YEAR.value:
                if negative:
                    options[param_key] = [random.choice([f'Release year should be the "'
                                                         f'{self._summarize_title_year(value)}".',
                                                         f'Need a movie from the "'
                                                         f'{self._summarize_title_year(value)}".'])]
                else:
                    options[param_key] = [random.choice([f'Release year shouldn\'t be the "'
                                                         f'{self._summarize_title_year(value)}".',
                                                         f'Don\'t need a movie from the "'
                                                         f'{self._summarize_title_year(value)}".'])]
            options.update({'/restart': ['/restart']})
        return options
