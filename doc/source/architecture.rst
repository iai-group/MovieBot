System Architecture
===================

This page provides a high-level overview of the architecture of our system.  At this level of abstraction, our system constitutes a domain-independent framework for facilitating conversational item recommendation.  Thus, even though we will be using movie-related examples for illustration, it is straightforward to adapt the system to other domains.

The system architecture is shown in the figure below, illustrating the core process for each dialogue turn.

.. image:: _static/Blueprint_MovieBot.png


Natural Language Understanding
------------------------------

The :py:class:`NLU <moviebot.nlu.nlu>` component converts the natural language :py:class:`UserUtterance <moviebot.utterance.utterance_user.UserUtterance>` into a :py:class:`DialogueAct <moviebot.dialogue_manager.dialogue_act>`. This process, comprising of *intent detection* and *slot filling*, is performed based on the current dialogue state.


Dialogue Manager
----------------

The :py:class:`DialogueManager <moviebot.dialogue_manager.dialogue_manager>` tracks the dialogue state and decides what action the system should take.  It consists of two sub-components:

- :py:class:`DialogueStateTracker <moviebot.dialogue_manager.dialogue_state_tracker>`, which updates the :py:class:`DialogueState <moviebot.dialogue_manager.dialogue_state>` and :py:class:`DialogueContext <moviebot.dialogue_manager.dialogue_context>` based on the dialogue acts by both the agent and the user.
- :py:class:`DialoguePolicy <moviebot.dialogue_manager.dialogue_policy>`, which generates a dialogue act by the agent based on the current dialogue state. It defines the flow of the conversation, i.e., what steps an agent must take at every stage.


Natural Language Generation
---------------------------

The :py:class:`NLG <moviebot.nlg.nlg>` component converts the output of the :py:class:`DialoguePolicy <moviebot.dialogue_manager.dialogue_policy>` to a natural language response.  Further, this component can (1) summarize the information need back to the user, to help them keep track of their stated preferences and (2) help the user to explore the item space by providing options.
