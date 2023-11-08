"""A rule-based policy developed as an initial step to generate action by the
agent based on the previous conversation and current dialogue."""


import random
from copy import deepcopy
from typing import Any, Dict, List

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.slots import Slots


class RuleBasedDialoguePolicy:
    def __init__(self, isBot: bool, new_user: bool) -> None:
        """Loads all necessary parameters for the policy.

        Args:
            isBot: If the conversation is via bot or not.
            new_user: Whether the user is new or not.
        """
        self.isBot = isBot
        self.new_user = new_user

    def _elict_dialogue_act(self, slot: str = None) -> DialogueAct:
        """Generates the elicitation dialogue act.

        Args:
            slot (optional): Slot to elicit. Defaults to None.

        Returns:
            Dialogue act.
        """
        return DialogueAct(
            AgentIntents.ELICIT,
            [ItemConstraint(slot, Operator.EQ, "")] if slot else [],
        )

    def _recommend_dialogue_act(self, name: str) -> DialogueAct:
        """Generates the recommend dialogue act.

        Args:
            name: Name of the movie to recommend.

        Returns:
            Dialogue act.
        """
        return DialogueAct(
            AgentIntents.RECOMMEND,
            [ItemConstraint(Slots.TITLE.value, Operator.EQ, name)],
        )

    def _get_welcome_dialogue_acts(
        self, dialogue_state: DialogueState, restart: bool = False
    ) -> List[DialogueAct]:
        """Generates the welcome dialogue act if applicable.

        Args:
            dialogue_state: Current dialogue state.

        Returns:
            A list with the welcome dialogue act.
        """
        if not dialogue_state.last_user_dacts and not restart:
            return [
                DialogueAct(
                    AgentIntents.WELCOME,
                    [
                        ItemConstraint("new_user", Operator.EQ, self.new_user),
                        ItemConstraint("is_bot", Operator.EQ, self.isBot),
                    ],
                )
            ]
        return []

    def _get_restart_dialogue_acts(
        self, dialogue_state: DialogueState, restart: bool = False
    ) -> List[DialogueAct]:
        """Generates the restart dialogue act if applicable.

        Args:
            dialogue_state: Current dialogue state.
            restart: Whether the user wants to restart the conversation.

        Returns:
            A list with the restart and elicitation dialogue acts.
        """
        if (not dialogue_state.last_user_dacts and restart) or (
            dialogue_state.last_user_dacts
            and UserIntents.RESTART
            in [dact.intent for dact in dialogue_state.last_user_dacts]
        ):
            return [
                DialogueAct(AgentIntents.RESTART, []),
                self._elict_dialogue_act(dialogue_state.agent_requestable[0]),
            ]
        return []

    def _get_bye_dialogue_acts(
        self, user_intents: set[UserIntents]
    ) -> List[DialogueAct]:
        """Generates the bye dialogue act if applicable.

        Args:
            user_intents: Set of user intents.

        Returns:
            List of dialogue acts.
        """
        if UserIntents.BYE in user_intents:
            return [DialogueAct(AgentIntents.BYE, [])]
        return []

    def _get_elicit_dialogue_acts(
        self,
        dialogue_state: DialogueState,
        user_intents: set[UserIntents],
        slots: List[str],
    ) -> List[DialogueAct]:
        """Generates the elicit dialogue acts if applicable.

        Args:
            dialogue_state: Current dialogue state.
            user_intents: Set of user intents.
            slots: List of slots.

        Returns:
            List of dialogue acts.
        """
        if user_intents.intersection(
            [
                UserIntents.ACKNOWLEDGE,
                UserIntents.UNK,
                UserIntents.HI,
            ]
        ) and AgentIntents.WELCOME in [
            dact.intent for dact in dialogue_state.last_agent_dacts
        ]:
            return [self._elict_dialogue_act(slots[0])]
        return []

    def _get_agent_made_partial_offer_dialogue_acts(
        self,
        dialogue_state: DialogueState,
        slots: List[str],
    ) -> List[DialogueAct]:
        """Generates the agent made partial offer dialogue acts if applicable.

        Args:
            dialogue_state: Current dialogue state.
            slots: List of slots.

        Returns:
            List of dialogue acts.
        """
        agent_dacts = []
        CIN_slots = [
            key
            for key in dialogue_state.frame_CIN.keys()
            if not dialogue_state.frame_CIN[key] and key != Slots.TITLE.value
        ]
        if (
            len(CIN_slots) >= dialogue_state.slot_left_unasked
        ):  # if there is a scope of
            # further questioning
            # results and will ask next question
            agent_dacts.append(
                DialogueAct(
                    AgentIntents.COUNT_RESULTS,
                    [
                        ItemConstraint(
                            "count",
                            Operator.EQ,
                            len(dialogue_state.database_result),
                        )
                    ],
                )
            )
            # adding another dialogue act of ELICIT
            slots_to_elicit = (
                [slot for slot in slots if not dialogue_state.frame_CIN[slot]]
                if not dialogue_state.agent_req_filled
                else CIN_slots,
            )
            agent_dacts.append(
                self._elict_dialogue_act(
                    random.choice(slots_to_elicit)[0]
                    if slots_to_elicit
                    else None
                )
            )

        else:
            agent_dacts.append(
                self._recommend_dialogue_act(
                    dialogue_state.database_result[0][Slots.TITLE.value]
                )
            )
        return agent_dacts

    def _get_agent_made_offer_dialogue_acts(
        self,
        dialogue_state: DialogueState,
        user_dact: DialogueAct,
    ) -> List[DialogueAct]:
        """Generates the agent made offer dialogue acts if applicable.

        Args:
            dialogue_state: Current dialogue state.
            slots: List of slots.

        Returns:
            List of dialogue acts.
        """
        agent_dacts = []
        if user_dact.intent == UserIntents.INQUIRE:
            params = [
                ItemConstraint(
                    param.slot,
                    Operator.EQ,
                    dialogue_state.item_in_focus[
                        Slots.TITLE.value
                        if param.slot == Slots.MORE_INFO.value
                        else param.slot
                    ],
                )
                for param in user_dact.params
            ] or [
                ItemConstraint(
                    "deny",
                    Operator.EQ,
                    dialogue_state.item_in_focus[Slots.TITLE.value],
                )
            ]
            agent_dacts.append(DialogueAct(AgentIntents.INFORM, params))
        elif user_dact.intent == UserIntents.ACCEPT:
            agent_dacts.append(
                DialogueAct(
                    AgentIntents.CONTINUE_RECOMMENDATION,
                    [
                        ItemConstraint(
                            Slots.TITLE.value,
                            Operator.EQ,
                            dialogue_state.item_in_focus[Slots.TITLE.value],
                        )
                    ],
                )
            )
        return agent_dacts

    def _get_elicit_or_recommend_dialogue_acts(
        self,
        dialogue_state: DialogueState,
        user_dact: DialogueAct,
        slots: List[str],
    ) -> List[DialogueAct]:
        """Generates the elicit or recommend dialogue acts if applicable.

        Args:
            dialogue_state: Current dialogue state.
            user_dact: User dialogue act.
            slots: List of slots.

        Returns:
            List of dialogue acts.
        """
        agent_dacts = []
        if (
            dialogue_state.agent_made_partial_offer
        ):  # agent will inform about number of
            agent_dacts.extend(
                self._get_agent_made_partial_offer_dialogue_acts(
                    dialogue_state, slots
                )
            )

        elif dialogue_state.agent_should_make_offer:
            agent_dacts.append(
                self._recommend_dialogue_act(
                    dialogue_state.item_in_focus[Slots.TITLE.value]
                )
            )
        elif dialogue_state.agent_offer_no_results:
            agent_dacts.append(DialogueAct(AgentIntents.NO_RESULTS, []))
        elif dialogue_state.agent_made_offer:
            agent_dacts.extend(
                self._get_agent_made_offer_dialogue_acts(
                    dialogue_state, user_dact
                )
            )

        return agent_dacts

    def _get_other_dialogue_acts(
        self,
        dialogue_state: DialogueState,
        user_dact: DialogueAct,
        slots: List[str],
    ) -> List[DialogueAct]:
        """Generates the other dialogue acts if applicable.

        Args:
            dialogue_state: Current dialogue state.
            user_dact: User dialogue act.
            slots: List of slots.

        Returns:
            List of dialogue acts.
        """
        if (
            not dialogue_state.agent_req_filled
            and user_dact.intent != UserIntents.HI
        ):
            # random.shuffle(slots)
            slot_to_elicit = next(
                (slot for slot in slots if not dialogue_state.frame_CIN[slot]),
                None,
            )
            return [self._elict_dialogue_act(slot_to_elicit)]
        elif user_dact.intent == UserIntents.UNK:
            return [DialogueAct(AgentIntents.CANT_HELP)]
        return []

    def next_action(
        self,
        dialogue_state: DialogueState,
        restart: bool = False,
    ) -> List[DialogueAct]:
        """Decides the next action to be taken by the agent based on the
        current state and context.

        Args:
            dialogue_state: Current dialogue state.
            restart: Whether or not to restart the dialogue. Defaults to False.

        Returns:
            A list of dialogue acts.
        """
        user_intents = (
            set(dact.intent for dact in dialogue_state.last_user_dacts)
            if dialogue_state.last_user_dacts
            else set()
        )
        slots = deepcopy(dialogue_state.agent_requestable)

        agent_dacts = (
            self._get_welcome_dialogue_acts(dialogue_state, restart)
            or self._get_restart_dialogue_acts(dialogue_state, restart)
            or self._get_bye_dialogue_acts(user_intents)
            or self._get_elicit_dialogue_acts(
                dialogue_state, user_intents, slots
            )
        )

        if agent_dacts:
            return agent_dacts

        for user_dact in dialogue_state.last_user_dacts:
            # deciding between intent "elicit" or "recommend"
            agent_dacts_for_user_dact = (
                self._get_elicit_or_recommend_dialogue_acts(
                    dialogue_state, user_dact, slots
                )
                or self._get_other_dialogue_acts(
                    dialogue_state, user_dact, slots
                )
            )
            agent_dacts.extend(agent_dacts_for_user_dact)

        if len(agent_dacts) == 0:
            agent_dacts.append(DialogueAct(AgentIntents.CANT_HELP, []))
        # Adding example:
        for agent_dact in agent_dacts:
            if agent_dact.intent == AgentIntents.ELICIT and agent_dact.params[
                0
            ].slot not in [Slots.YEAR.value]:
                if dialogue_state.database_result:
                    agent_dact.params[0].value = self._generate_examples(
                        dialogue_state.database_result,
                        agent_dact.params[0].slot,
                    )
        return agent_dacts

    def _generate_examples(
        self, database_result: List[Dict[str, Any]], slot: str
    ) -> str:
        """Generates a list of examples for specific slot.

        Args:
            database_result: The database results for a user information needs.
            slot: Slot to find examples for.

        Returns:
            A string with a list of examples for a slot.
        """
        examples = []
        for result in database_result:
            if slot not in result:
                continue

            temp_result = [x.strip() for x in result[slot].split(",")]
            examples.extend(
                [f"'{x}'" for x in temp_result if x not in examples]
            )
            if len(set(examples)) > 20:
                break

        examples = list(set(examples))
        if len(examples) == 1:
            return examples[0]
        elif len(examples) > 1:
            _sub_example = [x for x in examples if len(x.split()) == 2]
            if len(_sub_example) >= 2:
                return " or ".join(random.sample(_sub_example, 2))
            else:
                return " or ".join(random.sample(examples, 2))
