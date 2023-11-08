"""Dialogue state models the state of the agent.

It is a basic SlotFilling model that keeps account of the question
agents must answer or ask from the user. It also keeps track of the
recommendation agent makes and previous states of the agent. State will
be updated using the dialogue state tracker.
"""


from copy import deepcopy
from typing import Any, Dict, List

from moviebot.dialogue_manager.dialogue_act import DialogueAct
from moviebot.domain.movie_domain import MovieDomain


class DialogueState:
    def __init__(
        self, domain: MovieDomain, slots: List[str], isBot: bool
    ) -> None:
        """Initializes the SlotFilling dialogue state structures.

        Args:
            domain: Domain knowledge.
            slots: The slots to find information needs.
            isBot: If the conversation is via bot or not.
        """
        self.isBot = isBot
        self.domain = domain
        # the recommended movie and all it's attributes from the database
        self.item_in_focus = None
        # user requestable attributes of item_in_focus and system answers
        # self.requestable_slots_filled = {}
        self.agent_requestable = deepcopy(self.domain.agent_requestable)
        self.user_requestable = deepcopy(self.domain.user_requestable)
        self.frame_CIN = dict.fromkeys(slots)  # user requirements before
        # making a recommendation. CIN stands for current information needs
        self.frame_PIN = (
            {}
        )  # previous information needs of the user in case user want to go back
        self.prev_agent_dacts: List[DialogueAct] = []  # list of agent dacts
        # the current agent dact (singular, must be updated carefully)
        self.last_agent_dacts: DialogueAct = None
        self.last_user_dacts: List[DialogueAct] = None  # the current user act

        # Keep track of the recommended movies
        self.movies_recommended = {}

        self.is_beginning = True

    def _agent_offer_state(self) -> str:
        """Returns string representation of the agent's offer state."""
        offer_state = {
            "agent_req_filled": self.agent_req_filled,
            "agent_can_lookup": self.agent_can_lookup,
            "agent_made_partial_offer": self.agent_made_partial_offer,
            "agent_should_make_offer": self.agent_should_make_offer,
            "agent_made_offer": self.agent_made_offer,
            "agent_offer_no_results": self.agent_offer_no_results,
            # 'agent_repeats_offer' : self.agent_repeats_offer,
            "at_terminal_state": self.at_terminal_state,
        }
        return str([x for x, y in offer_state.items() if y])

    def to_dict(self) -> Dict[str, Any]:
        """Returns the dialogue state as a dictionary.

        Returns:
            Dictionary having basic info about the state.
        """
        dstate = {}
        dstate["Previous_Information_Need"] = str(
            {x: self.frame_PIN[x] for x, y in self.frame_PIN.items() if y}
        )
        dstate["User_Dialogue_Acts"] = (
            str([str(x) for x in self.last_user_dacts])
            if self.last_user_dacts
            else None
        )
        dstate["Current_Information_Needs"] = str(
            {x: self.frame_CIN[x] for x, y in self.frame_CIN.items() if y}
        )
        dstate["Agent_Dialogue_Acts"] = (
            str([str(x) for x in self.last_agent_dacts])
            if self.last_agent_dacts
            else None
        )
        dstate["Agent_Offer_State"] = self._agent_offer_state()
        dstate["Agent_Recommendations"] = str(self.movies_recommended)
        return dstate

    def __str__(self) -> str:
        """Returns the string representation of the dialogue state."""
        return str(self.to_dict())

    def initialize(self) -> None:
        """Initializes the state if the dialogue starts again."""
        # set the structure of CIN based of their value count
        for slot in self.frame_CIN:
            if slot in self.domain.multiple_values_CIN:
                self.frame_CIN[slot] = []
            else:
                self.frame_CIN[slot] = None
        # the recommended movie and all it's attributes from the database
        self.item_in_focus = None
        self.items_in_context = False
        self.movies_recommended = {}

        self.agent_requestable = deepcopy(self.domain.agent_requestable)
        self.user_requestable = deepcopy(self.domain.user_requestable)
        self.agent_req_filled = (
            False  # flag if the necessary information needs are filled
        )
        self.agent_can_lookup = (
            False  # flag if agent can offer based even if agent requirements
        )
        # are not filled
        self.agent_made_partial_offer = (
            False  # flag indicating if agent has results but needs to
        )
        # narrow it further down
        self.agent_should_make_offer = (
            False  # flag indicating if agent is going to make an offer
        )
        self.agent_should_offer_similar = False
        self.similar_movies = {}
        self.agent_made_offer = (
            False  # flag indicating if agent has made recommendation and it
        )
        # is being considered
        self.agent_offer_no_results = (
            False  # flag indicating if agent no results to offer
        )
        self.at_terminal_state = False  # the dialogue must end now
        # Assigning parameters for database results
        self.agent_must_clarify = (
            False  # flag if the same annotation is detected for two slots
        )
        self.dual_params = {}
        self.database_result = None
        self.max_db_result = 100
        self.slot_left_unasked = (
            3  # number of CIN slots which remain empty before agent must make
        )
        # an offer

        self.is_beginning = True
