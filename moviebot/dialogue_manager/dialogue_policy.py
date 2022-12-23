"""A rule-based policy developed as an initial step to generate action by the
agent based on the previous conversation and current dialogue."""


import random
from copy import deepcopy
from typing import List

from moviebot.core.intents.agent_intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_context import DialogueContext
from moviebot.dialogue_manager.dialogue_state import DialogueState
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.slots import Slots
from moviebot.ontology.ontology import Ontology


class DialoguePolicy:
    def __init__(self, ontology: Ontology, isBot: bool, new_user: bool):
        """Loads all necessary parameters for the policy.

        Args:
            ontology: Rules for the slots in the database.
            isBot: If the conversation is via bot or not.
            new_user: Whether the user is new or not.
        """
        self.ontology = ontology
        self.isBot = isBot
        self.new_user = new_user

    def next_action(  # noqa: C901
        self,
        dialogue_state: DialogueState,
        dialogue_context: DialogueContext = None,
        restart: bool = False,
    ) -> List[DialogueAct]:
        """Decides the next action to be taken by the agent based on the
        current state and context.

        Args:
            dialogue_state: Current dialogue state.
            dialogue_context: Context of the dialogue. Defaults to None.
            restart: Whether or not to restart the dialogue. Defaults to False.

        Returns:
            A list of dialogue acts.
        """
        agent_dacts = []
        slots = deepcopy(dialogue_state.agent_requestable)
        if not dialogue_state.last_user_dacts and not restart:
            agent_dacts.append(
                DialogueAct(
                    AgentIntents.WELCOME,
                    [
                        ItemConstraint("new_user", Operator.EQ, self.new_user),
                        ItemConstraint("is_bot", Operator.EQ, self.isBot),
                    ],
                )
            )
            return agent_dacts

        if not dialogue_state.last_agent_dacts and not restart:
            if not dialogue_state.last_agent_dacts:
                agent_dacts.append(
                    DialogueAct(
                        AgentIntents.WELCOME,
                        [
                            ItemConstraint(
                                "new_user", Operator.EQ, self.new_user
                            ),
                            ItemConstraint("is_bot", Operator.EQ, self.isBot),
                        ],
                    )
                )

        if (not dialogue_state.last_user_dacts and restart) or (
            dialogue_state.last_user_dacts
            and UserIntents.RESTART
            in [dact.intent for dact in dialogue_state.last_user_dacts]
        ):
            agent_dacts.append(DialogueAct(AgentIntents.RESTART, []))
            agent_dacts.append(
                DialogueAct(
                    AgentIntents.ELICIT,
                    [ItemConstraint(slots[0], Operator.EQ, "")],
                )
            )
            return agent_dacts

        for user_dact in dialogue_state.last_user_dacts:
            agent_dact = DialogueAct(AgentIntents.UNK, [])
            # generating intent = "bye"
            if user_dact.intent == UserIntents.BYE:
                agent_dact.intent = AgentIntents.BYE
                agent_dacts.append(deepcopy(agent_dact))
                return agent_dacts

            # generating intent = "elicit"
            if (
                user_dact.intent == UserIntents.ACKNOWLEDGE
                or user_dact.intent == UserIntents.UNK
            ):
                if AgentIntents.WELCOME in [
                    dact.intent for dact in dialogue_state.last_agent_dacts
                ]:
                    agent_dact.intent = AgentIntents.ELICIT
                    agent_dact.params.append(
                        ItemConstraint(slots[0], Operator.EQ, "")
                    )
                    agent_dacts.append(deepcopy(agent_dact))
                    return agent_dacts

            # deciding between intent "elicit" or "recommend"
            if (
                dialogue_state.agent_made_partial_offer
            ):  # agent will inform about number of
                CIN_slots = [
                    key
                    for key in dialogue_state.frame_CIN.keys()
                    if not dialogue_state.frame_CIN[key]
                    and key != Slots.TITLE.value
                ]
                if (
                    len(CIN_slots) >= dialogue_state.slot_left_unasked
                ):  # if there is a scope of
                    # further questioning
                    # results and will ask next question
                    agent_dact.intent = AgentIntents.COUNT_RESULTS
                    agent_dact.params.append(
                        ItemConstraint(
                            "count",
                            Operator.EQ,
                            len(dialogue_state.database_result),
                        )
                    )
                    agent_dacts.append(deepcopy(agent_dact))
                    # adding another dialogue act of ELICIT
                    if dialogue_state.agent_req_filled:
                        random.shuffle(CIN_slots)
                        agent_dact = DialogueAct(AgentIntents.ELICIT, [])
                        agent_dact.params.append(
                            ItemConstraint(CIN_slots[0], Operator.EQ, "")
                        )
                        agent_dacts.append(deepcopy(agent_dact))
                    else:
                        agent_dact = DialogueAct(AgentIntents.ELICIT, [])
                        random.shuffle(slots)
                        for slot in slots:
                            if not dialogue_state.frame_CIN[slot]:
                                agent_dact.params.append(
                                    ItemConstraint(slot, Operator.EQ, "")
                                )
                                break
                        agent_dacts.append(deepcopy(agent_dact))

                else:
                    agent_dact = DialogueAct(AgentIntents.RECOMMEND, [])
                    item_in_focus = dialogue_state.database_result[0]
                    agent_dact.params.append(
                        ItemConstraint(
                            Slots.TITLE.value,
                            Operator.EQ,
                            item_in_focus[Slots.TITLE.value],
                        )
                    )
            elif dialogue_state.agent_should_make_offer:
                agent_dact.intent = AgentIntents.RECOMMEND
                agent_dact.params.append(
                    ItemConstraint(
                        Slots.TITLE.value,
                        Operator.EQ,
                        dialogue_state.item_in_focus[Slots.TITLE.value],
                    )
                )
                agent_dacts.append(deepcopy(agent_dact))
            elif dialogue_state.agent_offer_no_results:
                agent_dact.intent = AgentIntents.NO_RESULTS
                agent_dacts.append(deepcopy(agent_dact))
            elif dialogue_state.agent_made_offer:
                if user_dact.intent == UserIntents.INQUIRE:
                    agent_dact.intent = AgentIntents.INFORM
                    for param in user_dact.params:
                        if param.slot != Slots.MORE_INFO.value:
                            agent_dact.params.append(
                                ItemConstraint(
                                    param.slot,
                                    Operator.EQ,
                                    dialogue_state.item_in_focus[param.slot],
                                )
                            )
                        else:
                            agent_dact.params.append(
                                ItemConstraint(
                                    param.slot,
                                    Operator.EQ,
                                    dialogue_state.item_in_focus[
                                        Slots.TITLE.value
                                    ],
                                )
                            )
                    if len(agent_dact.params) == 0:
                        agent_dact.params.append(
                            ItemConstraint(
                                "deny",
                                Operator.EQ,
                                dialogue_state.item_in_focus[Slots.TITLE.value],
                            )
                        )
                    agent_dacts.append(deepcopy(agent_dact))
                # elif (
                #     user_dact.intent == UserIntents.REVEAL
                #     and Slots.TITLE.value
                #     in [param.slot for param in user_dact.params]
                # ):
                #     agent_dact.intent = AgentIntents.INFORM
                #     agent_dact.params.append(
                #         ItemConstraint(
                #             Slots.MORE_INFO.value,
                #             Operator.EQ,
                #             dialogue_state.item_in_focus[Slots.TITLE.value],
                #         )
                #     )
                #     agent_dacts.append(deepcopy(agent_dact))
                elif user_dact.intent == UserIntents.ACCEPT:
                    agent_dact.intent = AgentIntents.CONTINUE_RECOMMENDATION
                    agent_dact.params.append(
                        ItemConstraint(
                            Slots.TITLE.value,
                            Operator.EQ,
                            dialogue_state.item_in_focus[Slots.TITLE.value],
                        )
                    )
                    agent_dacts.append(deepcopy(agent_dact))

            if agent_dact.intent == AgentIntents.UNK:
                if (
                    not dialogue_state.agent_req_filled
                    and user_dact.intent != UserIntents.HI
                ):
                    agent_dact.intent = AgentIntents.ELICIT
                    # random.shuffle(slots)
                    for slot in slots:
                        if not dialogue_state.frame_CIN[slot]:
                            agent_dact.params.append(
                                ItemConstraint(slot, Operator.EQ, "")
                            )
                            break
                elif user_dact.intent == UserIntents.UNK:
                    agent_dact.intent = AgentIntents.CANT_HELP
                if agent_dact.intent != AgentIntents.UNK:
                    agent_dacts.append(deepcopy(agent_dact))

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

    def _generate_examples(self, database_result: List, slot: str) -> str:
        """Generates a list of examples for specific slot.

        Args:
            database_result: The database results for a user information needs.
            slot: Slot to find examples for.

        Returns:
            A string with a list of examples for a slot.
        """
        examples = []
        for result in database_result:
            temp_result = [x.strip() for x in result[slot].split(",")]
            examples.extend(
                [f"'{x}'" for x in temp_result if x not in examples]
            )
            if len(set(examples)) > 20:
                break
        if examples:
            examples = list(set(examples))
            random.shuffle(examples)
            if len(examples) == 1:
                return examples[0]
            _sub_example = [x for x in examples if len(x.split()) == 2]
            if len(_sub_example) >= 2:
                return " or ".join(random.sample(_sub_example, 2))
            else:
                return " or ".join(random.sample(examples, 2))
