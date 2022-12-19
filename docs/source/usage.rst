Usage
=====

Running IAI MovieBot
--------------------


* A YAML configuration file is necessary to start the MovieBot, see example `config/moviebot_config.yaml`. 
* Execute the command below to run the MovieBot.

.. code-block:: shell

   $ python -m moviebot.run -c <path_to_config.yaml>
       

Note: To create Slot-Values, execute the code once by setting `BOT: False` in the configuration file.

Quickstart IAI MovieBot in the console
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run MovieBot with default configuration execute the command below.

.. code-block:: shell

   $ python -m moviebot.run -c config/moviebot_config.yaml

Quickstart IAI MovieBot with Telegram
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run MovieBot with Telegram you need to create a configuration file as below.
Then, you can run the command to start the MovieBot with this file.

.. code-block:: yaml

   ---

   CONVERSATION_LOGS: # implementation: save conversational logs for debugging
      save: False
      nlp: True
      path: reports/conversations/

   DATA:
   ontology_path: data/movies_ontology.json
   db_path: data/movies_dbase.db
   slot_values_path: data/slot_values.json

   NLU:
   tag_words_slots: config/tag_words_slots.json

   TELEGRAM: True # execute the code on Telegram

   POLLING: True # True when using Telegram without server

   BOT_TOKEN_PATH: config/bot_token.yaml

   BOT_HISTORY: # save the conversational logs for Telegram users
      save: True
      path: conversation_history/

   DEBUG: False

