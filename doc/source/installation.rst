Installation
============

Telegram Bot Token
------------------
- To use Telegram, one must install the Telegram application available `here <https://telegram.org/>`_.
- Click `here <https://core.telegram.org/bots#6-botfather>`_ for instructions about how to create a Telegram Bot.
- Add the token of the new bot to the `Telegram Bot Token <config/bot_token.yaml>`_ file as ``BOT_TOKEN: <<token>>``.

Conversation History folder
---------------------------

Create a folder named `conversation_history`. The conversational logs will be saved in this folder if allowed in the config file. These logs will be created when the *IAI MovieBot* is being executed on Telegram.


Python Libraries
----------------

- Execute the following commands to install necessary libraries for *IAI MovieBot*

    pip install pyyaml
    pip install python-telegram-bot --upgrade
    pip install wikipedia
    pip install nltk
       
nltk Resources
--------------

    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('stopwords')