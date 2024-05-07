Installation
============

The IAI MovieBot can run in the console and on Telegram.
To run the MovieBot in the console you only need to install the necessary Python libraries and nltk resources.
:ref:`Additional installation steps <_telegram_installation>` are needed to run MovieBot on Telegram: install Telegram and set up a bot.

Python Libraries
----------------

Execute the following commands to install the necessary libraries for IAI MovieBot


.. code-block:: shell

    $ pip3 install -r requirements.txt
       
nltk Resources
--------------

After installing the necessary libraries, you need to download nltk resources.
To do so run the following code in a Python console.

.. code-block:: python

    import nltk
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('stopwords')
    nltk.download('omw-1.4')

.. _telegram_installation::

Extra steps for Telegram 
------------------------

Telegram Bot Token
""""""""""""""""""
- To use Telegram, one must install the Telegram application available `here <https://telegram.org/>`_.
- Click `here <https://core.telegram.org/bots#6-botfather>`_ for instructions about how to create a Telegram Bot.
- Add the token of the new bot to the `Telegram Bot Token <config/bot_token.yaml>`_ file as ``BOT_TOKEN: <<token>>``.

Conversation History folder
"""""""""""""""""""""""""""

Create a folder named `conversation_history`. The conversational logs will be saved in this folder if allowed in the config file. These logs will be created when the IAI MovieBot is being executed on Telegram.
