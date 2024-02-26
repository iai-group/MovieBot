IAI MovieBot |release| documentation
=====================================

IAI MovieBot is a conversational recommender system for movies. It follows a standard task-oriented dialogue system architecture, comprising natural language understanding (NLU), dialogue manager (DM), and natural language generation (NLG) components. Additionally, it includes a user model and a recommendation engine. Some modules may use different models, which can be trained using the provided training utilities. It also comes with different deployment platforms (such as Telegram and Flask REST).
The distinctive features of IAI MovieBot include a task-specific dialogue flow, a multi-modal chat interface, and an effective way to deal with dynamically changing user preferences. While our current focus is limited to movies, the system aims to be a reusable and extensible development framework that can support users in accomplishing recommendation-related goals via multi-turn conversations.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   installation
   usage
   architecture
   dialogue
   reinforcement_learning


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


