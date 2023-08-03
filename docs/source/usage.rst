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

   $ python -m moviebot.run

Quickstart IAI MovieBot with Flask
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MovieBot can be deployed with Flask as a web application using REST or SocketIO.
You need to create a configuration file as below. Then, you can run the command to start the MovieBot with this file.

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

   RECOMMENDER: "slot_based"

   TELEGRAM: False # execute the code on Telegram

   POLLING: False # True when using Telegram without server

   BOT_TOKEN_PATH: config/bot_token.yaml

   BOT_HISTORY: # save the conversational logs for Telegram users
      save: True
      path: conversation_history

   DEBUG: False

Flask REST API
""""""""""""""

To run MovieBot with Flask REST API, you need to add the following line to the configuration file: `FLASK_REST: True`.

By default, MovieBot will be running locally on the port 5001. To modify the host or the port, you need to modify the file `moviebot/controller/server_rest.py`.

We do not provide a web client to interact with MovieBot. The communication is performed through HTTP requests.
The following example shows how to start a conversation with the MovieBot using Python:

.. code-block:: python

   import requests
   from pprint import pprint

   uri = "http://127.0.0.1:5001"

   # Start a new conversation
   r = requests.post(
            uri,
            json={
                     "message": {"text": "/start"},
                     "sender": {"id": "test_user"}, 
            },
        )
   pprint(r.json())
   >>> {'message': {'attachments': None,
             'intent': '',
             'text': 'Hi there. I am IAI MovieBot, your movie recommending '
                     'buddy. I can recommend you movies based on your '
                     'preferences.\n'
                     'I will ask you a few questions and based on your '
                     'answers, I will try to find a movie for you.\n'
                     '\n'
                     '\n'
                     '\n'
                     'INSTRUCTIONS\n'
                     '\n'
                     'To start the conversation say Hi or Hello, or simply '
                     'enter you preferences ("I want a horror movie from the '
                     '90s").\n'
                     '\n'
                     'To restart the recommendation process, issue '
                     '"/restart".\n'
                     '\n'
                     'To end the conversation, issue "/exit" or say '
                     'Bye/Goodbye.\n'
                     '\n'
                     'To see these instructions again, issue: "/help".'},
        'recipient': {'id': 'test_user'}}

Please note that in this configuration, the first message must be a `/start` message.

Flask SocketIO
""""""""""""""

To run MovieBot with Flask SocketIO, you need to add the following line to the configuration file: `FLASK_SOCKET: True`.

By default, MovieBot will be running locally on the port 5000. To modify the host or the port, you need to modify the file `moviebot/controller/server_socket.py`.

We provide a simple `web widget <https://www.npmjs.com/package/iaigroup-chatwidget>`_ to interact with the MovieBot. It can be added to any web page by adding the following lines to the associated HTML code:

.. code-block:: HTML

   <script type="text/javascript"
        src="https://cdn.jsdelivr.net/npm/iaigroup-chatwidget@1.1.2/build/bundle.min.js"></script>
    <script type="text/javascript">
        ChatWidget({
            name: "MovieBot",
            serverUrl: "http://127.0.0.1:5001",
            socketioPath: "/socket.io/",
            useFeedback: false,
            useLogin: false,
        });
    </script>

A button to interact with MovieBot should be placed at the bottom right of your web page.

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

