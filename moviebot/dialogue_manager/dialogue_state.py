"""DialogueState models the state of the agent. It is a basic SlotFilling model
that keeps account of the question agents must answer or ask from the user. It
also keeps track of the recommendation agent makes and previous states of the
agent. State will be updated using the Dialogue State Tracker.
"""


from copy import deepcopy

from moviebot.ontology.ontology import Ontology


class DialogueState:
    """DialogueState models the state of the agent. It is a basic SlotFilling
    model that keeps account of the question agents must answer or ask from the
    user. It also keeps track of the recommendation agent makes and previous
    states of the agent. State will be updated using the Dialogue State Tracker.
    """

    def __init__(self, ontology, slots, isBot):
        """Initializes the Slot Filling Dialogue State structures

        :type ontology: Ontology

        Args:
            ontology: the ontology of the domain
            slots: the slots to find information needs
            isBot: if the conversation is via bot or not

        """
        self.isBot = isBot
        self.ontology = ontology
        self.item_in_focus = None  # the recommended movie and all it's attributes from the database
        # self.requestable_slots_filled = {} # user requestable attributes of item_in_focus and
        # system answers
        self.agent_requestable = deepcopy(self.ontology.agent_requestable)
        self.user_requestable = deepcopy(self.ontology.user_requestable)
        self.frame_CIN = dict.fromkeys(slots)  # user requirements before
        # making a recommendation. CIN stands for current information needs
        self.frame_PIN = (
            {}
        )  # previous information needs of the user in case user want to go back
        self.prev_agent_dacts = []  # list of agent dacts
        self.last_agent_dacts = (
            None  # the current agent dact (singular, must be updated carefully)
        )
        self.last_user_dacts = None  # the current user act

    def _agent_offer_state(self):
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

    def _dict(self):
        """Prints the state to debug the position of the agent.

        Returns:
            a string having basic info about the state

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
        return dstate

    def __str__(self):
        return str(self._dict())

    def initialize(self):
        """Initializes/resets the state if the dialogue starts again."""
        # set the structure of CIN based of their value count
        for slot in self.frame_CIN:
            if slot in self.ontology.multiple_values_CIN:
                self.frame_CIN[slot] = []
            else:
                self.frame_CIN[slot] = None
        self.item_in_focus = None  # the recommended movie and all it's attributes from the database
        self.items_in_context = False
        self.agent_requestable = deepcopy(self.ontology.agent_requestable)
        self.user_requestable = deepcopy(self.ontology.user_requestable)
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
