Installation
============

Telegram Bot Token
------------------
- To use Telegram, one must install the Telegram application available `here <https://telegram.org/>`_.
- Click `here <https://core.telegram.org/bots#6-botfather>`_ for instructions about how to create a Telegram Bot.
- Add the token of the new bot to the `Telegram Bot Token <config/bot_token.yaml>`_ file as ``BOT_TOKEN: <<token>>``.

Messenger
------------------
- Create a facebook developer account.
- Set up a facebook page with a regular facebook account.
- Create a new messenger app and connect it to the facebook page.
- In the app settings page, click 'Generate Token'. Add this token to MESSENGER_TOKEN: <<token>> in <config/bot_token.yaml>.
- In the app settings page, click 'Edit Callback URL'. Add a webhook URL and a verify token of your choice. 
- For the webhook URL a port forwarding service like ngrok can be used.
- Add the verify token to MESSENGER_VERIFY_TOKEN: <<token>> in <config/bot_token.yaml>.

Conversation History folder
---------------------------

Create a folder named `conversation_history`. The conversational logs will be saved in this folder if allowed in the config file. These logs will be created when the IAI MovieBot is being executed on Telegram.


Python Libraries
----------------

- Execute the following commands to install necessary libraries for IAI MovieBot


.. code-block:: shell

    $ pip3 install -r requirements.txt
       
nltk Resources
--------------

.. code-block:: python

    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('stopwords')