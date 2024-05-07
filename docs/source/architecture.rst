System Architecture
===================

This page provides a high-level overview of the architecture of our system.  At this level of abstraction, our system constitutes a domain-independent framework for facilitating conversational item recommendation.  Thus, even though we will be using movie-related examples for illustration, it is straightforward to adapt the system to other domains.

The overview of the system architecture is shown in the figure below.

.. image:: _static/Blueprint_MovieBot_v2.png

The main components of the system are:

- :doc:`Natural Language Understanding <nlu>`
- Dialogue Manager
- Natural Language Generation

Dialogue Manager
----------------

This component keeps track of the dialogue state and context, in addition to deciding the next action the system should take.
Please refer to the :doc:`dialogue manager <dialogue_manager>` section for a detailed description.

Natural Language Generation
---------------------------

The :py:class:`NLG <moviebot.nlg.nlg>` component converts the output of the :py:class:`DialoguePolicy <moviebot.dialogue_manager.dialogue_policy>` to a natural language response.  Further, this component can (1) summarize the information need back to the user, to help them keep track of their stated preferences and (2) help the user to explore the item space by providing options.
