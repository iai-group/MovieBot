# *IAI MovieBot* movie recommender system
This is v0.1.

*IAI MovieBot* is an open-source, conversational movie recommender system which models users
' preferences dynamically and supports user initiatives and multi-turn recommendations.
*IAI MovieBot* equips with a scaleable structure for future amendments.
It facilities the standardized components.
In specific, intent recognition in NLU identifies users' intent based on preferences and
 recognizes entities (movies and attributes) for users' utterances, NLG generates natural language responses based on templates, and dialogue policy in the dialogue manager adapts to the users' requirements in the conversation.

The main architecture is shown in the figure below. A multi-turn conversation is initiated and terminated by the users. The users' response is processed by the NLU. The DM receives the users' dialogue acts from the NLU and generates the agent's dialogue acts. Based on the act from DM, the NLG generates a natural response to the users. This loop happens for each turn in the conversation.


![A sample dialogue in IAI MovieBot](doc/Blueprint_MovieBot.png)

## Main Components in *IAI MovieBot*:
- [Controller](iaibot/controller/controller.py)
  - [Controller Telegram Bot](iaibot/controller/controller_bot.py)
  - [Controller Terminal](iaibot/controller/controller_terminal.py)
- [Conversational Agent](iaibot/agent/agent.py)
  - [Natural Language Understanding](iaibot/nlu/nlu.py)
    - [Intents Detection](iaibot/nlu/user_intents_checker.py)
    - [Slot Filling](iaibot/nlu/slot_annotator.py)
    - [Data Loader](iaibot/nlu/data_loader.py)
  - [Natural Language Generation](iaibot/nlg/nlg.py)
  - [Dialogue Manager](iaibot/dialogue_manager/dialogue_manager.py)
    - [Dialogue State Tracker](iaibot/dialogue_manager/dialogue_state_tracker.py)
      - [Dialogue State](iaibot/dialogue_manager/dialogue_state.py)
      - [Dialogue Context](iaibot/dialogue_manager/dialogue_context.py)
    - [Dialogue Policy](iaibot/dialogue_manager/dialogue_policy.py)
    - [Dialogue Act](iaibot/dialogue_manager/dialogue_act.py)
      - [Item Constraints](iaibot/dialogue_manager/item_constraint.py)
      - [Slots](iaibot/dialogue_manager/slots.py)
      - [Operator](iaibot/dialogue_manager/operator.py)
      - [Values](iaibot/dialogue_manager/values.py)
- Intents
   - [User Intents](iaibot/intents/user_intents.py)
   - [Agent Intents](iaibot/intents/agent_intents.py)
 - Database/Ontology
   - [Database](iaibot/database/database.py)
   - [Ontology](iaibot/ontology/ontology.py)

## Data and Configuration files in *IAI MovieBot*:
- [Configuration](data_and_config/config/moviebot_config.yaml): This file defines the basic
 configuration of *IAI MovieBot* including the paths to database, ontology and the token of Telegram Bot.
- [Telegram Bot Token](data_and_config/config/bot_token.yaml): This file should contain the
 Telegram Bot Token in the following format:

        BOT_TOKEN: <<token>>

- [Tag words for NLU](data_and_config/config/tag_words_slots.json): The designed patters for
 detection of slots in NLU are defined in this file.
- [MySQL Database](data_and_config/data/movies_dbase.db)
- [Ontology](data_and_config/data/movies_ontology.json)
- [Slot-Values](data_and_config/data/slot_values.json): This file must be created by the NLU

## *IAI MovieBot* Installation

### Telegram Bot Token
- To use Telegram, one must install the Telegram application available [here](https://telegram.org/).
- Click [here](https://core.telegram.org/bots#6-botfather) for instructions about how to create a Telegram Bot.
- Add the token of the new bot to the [Telegram Bot Token](data_and_config/config/bot_token.yaml
) file as ``BOT_TOKEN: <<token>>``.

### Conversation History folder
Create a folder named `conversation_history`. The conversational logs will be saved in this folder if allowed in the config file. These logs will be created when the *IAI MovieBot* is being executed on Telegram.


### Python Libraries
- Execute the following commands to install necessary libraries for *IAI MovieBot*

       pip install pyyaml
       pip install python-telegram-bot --upgrade
       pip install wikipedia
       pip install nltk
       
### nltk Resources
       nltk.download('punkt')
       nltk.download('wordnet')
       nltk.download('stopwords')
	   
## Running *IAI MovieBot*

       python iai_bot.py -c <path_to_config.yaml>
       
Note: To create Slot-Values, execute the code once by setting `BOT: False` n the configuration file.
