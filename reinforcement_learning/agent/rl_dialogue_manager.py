"""Dialogue manager used when training a dialogue policy with RL."""


import logging
from typing import Any, Dict, List

from moviebot.core.intents import AgentIntents
from moviebot.core.intents.user_intents import UserIntents
from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.dialogue_manager.dialogue_manager import DialogueManager
from moviebot.nlu.annotation.item_constraint import ItemConstraint
from moviebot.nlu.annotation.operator import Operator
from moviebot.nlu.annotation.slots import Slots


class DialogueManagerRL(DialogueManager):
    def initialize(self) -> None:
        """Initializes the dialogue manager."""
        self.dialogue_state_tracker.initialize()

    def recommend(self) -> Dict[str, Any]:
        """Recommends a movie and updates state.

        Returns:
            Recommended movie.
        """
        # accesses the database to fetch results if required
        recommended_movies = self.recommender.recommend_items(self.get_state())

        self.dialogue_state_tracker.update_state_db(
            recommended_movies,
            self.recommender.get_previous_recommend_items(),
        )
        if recommended_movies:
            self.dialogue_state_tracker.dialogue_state.item_in_focus = (
                recommended_movies[0]
            )
            return recommended_movies[0]
        return None

    def replace_placeholders(
        self,
        dialogue_act: DialogueAct,
        user_dialogue_acts: List[DialogueAct],
        recommendation: Dict[str, Any],
    ) -> DialogueAct:
        """Replaces the placeholders in the dialogue act with actual values.

        Args:
            dialogue_act: Dialogue act.
            user_dialogue_acts: User dialogue acts.
            recommendation: Recommended movie.

        Returns:
            Dialogue act with placeholders replaced.
        """
        if (
            dialogue_act.intent == AgentIntents.RECOMMEND
            or dialogue_act.intent == AgentIntents.CONTINUE_RECOMMENDATION
        ):
            dialogue_act.params = [
                ItemConstraint(
                    Slots.TITLE.value,
                    Operator.EQ,
                    recommendation[Slots.TITLE.value],
                )
            ]
        elif dialogue_act.intent == AgentIntents.INFORM:
            for user_dact in user_dialogue_acts:
                if user_dact.intent == UserIntents.INQUIRE:
                    params = [
                        ItemConstraint(
                            param.slot,
                            Operator.EQ,
                            recommendation[
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
                            recommendation[Slots.TITLE.value],
                        )
                    ]
                    dialogue_act.params = params
        elif dialogue_act.intent == AgentIntents.COUNT_RESULTS:
            results = self.get_state().database_result
            dialogue_act.params = [
                ItemConstraint(
                    "count", Operator.EQ, len(results) if results else 0
                )
            ]
        return dialogue_act

    def get_filled_dialogue_acts(
        self, dialogue_acts: List[DialogueAct]
    ) -> List[DialogueAct]:
        """Returns the dialogue acts with filled placeholders.

        For example, if the agent replies with a dialogue act with the intent
        RECOMMEND, the title will be added as a constraint to the dialogue act:
        DialogueAct(
            AgentIntents.RECOMMEND,
            [ItemConstraint("title", Operator.EQ,"The Matrix")]
        )

        Args:
            dialogue_acts: Dialogue acts.

        Raises:
            Exception: If the dialogue act cannot be filled.

        Returns:
            Dialogue acts with filled placeholders.
        """
        filled_dialogue_acts = []

        recommendation = (
            self.recommend()
            if AgentIntents.RECOMMEND in [dact.intent for dact in dialogue_acts]
            else self.get_state().item_in_focus
        )

        user_dacts = self.get_state().last_user_dacts
        for dialogue_act in dialogue_acts:
            try:
                _dialogue_act = self.replace_placeholders(
                    dialogue_act, user_dacts, recommendation
                )
                filled_dialogue_acts.append(_dialogue_act)
            except Exception as e:
                logging.error(e, exc_info=True)
        return filled_dialogue_acts
