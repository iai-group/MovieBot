"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using Telegram."""

__author__ = "Javeria Habib"

import json
import logging
import os
import time
from copy import deepcopy

import yaml
from moviebot.agent.agent import Agent
from moviebot.controller.controller import Controller
from moviebot.core.shared.utterance.utterance import UserUtterance
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
CONTINUE = range(1)


class ControllerTelegram(Controller):
    """This is the Controller class which controls the flow of the conversation
    while the user interacts with the agent using telegram."""

    def __init__(self):
        """Initializes some basic structs for the Controller."""
        self.agent = {}
        self.configuration = None
        self.user_options = {}
        self.response = {}
        self.record_data_agent = {}
        self.record_data = {}
        self.token = ""

    def load_bot_token(self, bot_token_path):
        """Loads the Token for the Telegram bot

        :return: the token of the Telegram Bot

        Args:
            bot_token_path:

        """
        if isinstance(bot_token_path, str):
            if os.path.isfile(bot_token_path):
                with open(bot_token_path, "r") as file:
                    token_config = yaml.load(file, Loader=yaml.Loader)
                    if "BOT_TOKEN" in token_config:
                        return token_config["BOT_TOKEN"]
                    else:
                        raise ValueError(
                            "The token for Telegram bot is not found in the"
                            f" file {bot_token_path}"
                        )
            else:
                raise FileNotFoundError(f"File {bot_token_path} not found")
        else:
            raise ValueError("Unacceptable type of Token file name")

    def start(self, update, context):
        """Starts the conversation. This indicates initializing the components
        and start the conversation from scratch and identifying if the users are
        new or have used this system before.

        Args:
            update:
            context:

        """
        # create a new agent
        user_id = str(update.effective_user["id"])
        if user_id not in self.configuration["new_user"] or self.configuration[
            "new_user"
        ].get(user_id):
            self.configuration["new_user"].update(
                {user_id: self.new_user(user_id)}
            )
        self.agent[user_id] = Agent(self.configuration)
        self.user_options[user_id] = {}
        self.agent[user_id].initialize(user_id)
        print(
            f"Conversation is starting for user id = {user_id} and user name ="
            f" '{update.effective_user['first_name']}'"
        )
        (
            self.response[user_id],
            self.record_data_agent[user_id],
            _,
        ) = self.agent[user_id].start_dialogue(
            user_fname=update.effective_user["first_name"]
        )
        if self.configuration["new_user"][user_id]:
            update.message.reply_text(
                self._instruction(), parse_mode=ParseMode.MARKDOWN
            )
        update.message.reply_text(
            self.response[user_id],
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN,
        )
        # record the conversation
        if self.agent[user_id].bot_recorder:
            self.record_data[user_id] = {
                "Timestamp": str(update.message.date),
                "User_Input": update.message.text,
            }
            self.record_data[user_id].update(self.record_data_agent[user_id])
            self.agent[user_id].bot_recorder.record_user_data(
                user_id, self.record_data[user_id]
            )
        return CONTINUE

    def help(self, update, context):
        """Sends the users the instructions if they ask for help

        Args:
            update:
            context:

        """
        update.message.reply_text(
            self._instruction(help=True), parse_mode=ParseMode.MARKDOWN
        )
        return CONTINUE

    def restart(self, update, context):
        """Restarts the conversation. This is similar to start function.
        However, it starts the conversation with a welcome message and elicits
        the uses to begin with.

        Args:
            update:
            context:

        """
        # create a new agent
        user_id = str(update.effective_user["id"])
        if user_id not in self.configuration["new_user"] or self.configuration[
            "new_user"
        ].get(user_id):
            self.configuration["new_user"].update(
                {user_id: self.new_user(user_id)}
            )
        self.agent[user_id] = Agent(self.configuration)
        self.user_options[user_id] = {}
        self.agent[user_id].initialize(user_id)
        print(
            f"Conversation is starting for user id = {user_id} and user name ="
            f" '{update.effective_user['first_name']}'"
        )
        (
            self.response[user_id],
            self.record_data_agent[user_id],
            _,
        ) = self.agent[user_id].start_dialogue(
            user_fname=update.effective_user["first_name"], restart=True
        )
        if self.configuration["new_user"][user_id]:
            update.message.reply_text(
                self._instruction(), parse_mode=ParseMode.MARKDOWN
            )
        update.message.reply_text(
            self.response[user_id], reply_markup=ReplyKeyboardRemove()
        )
        # record the conversation
        if self.agent[user_id].bot_recorder:
            self.record_data[user_id] = {
                "Timestamp": str(update.message.date),
                "User_Input": update.message.text,
            }
            self.record_data[user_id].update(self.record_data_agent[user_id])
            self.agent[user_id].bot_recorder.record_user_data(
                user_id, self.record_data[user_id]
            )
        return CONTINUE

    def continue_conv(self, update, context):
        """Continues the conversation until the users want to restart of exit.

        Args:
            update:
            context:

        """
        user_id = str(update.effective_user["id"])
        if user_id not in self.configuration["new_user"] or self.configuration[
            "new_user"
        ].get(user_id):
            self.configuration["new_user"].update(
                {user_id: self.new_user(user_id)}
            )
        if user_id not in self.agent:
            self.agent[user_id] = Agent(self.configuration)
            self.user_options[user_id] = {}
            self.agent[user_id].initialize(user_id)
            self.agent[
                user_id
            ].dialogue_manager.dialogue_state_tracker.dialogue_state.initialize()
            self.agent[
                user_id
            ].dialogue_manager.dialogue_state_tracker.dialogue_context.initialize()
            print(
                f"Conversation is starting for user id = {user_id} and user"
                f" name = '{update.effective_user['first_name']}'"
            )
        start = time.time()
        user_utterance = UserUtterance(update.message.to_dict())
        (
            self.response[user_id],
            self.record_data_agent[user_id],
            self.user_options[user_id],
        ) = self.agent[user_id].continue_dialogue(
            user_utterance,
            self.user_options[user_id],
            user_fname=update.effective_user["first_name"],
        )
        if self.user_options[user_id]:
            # d = {str(key):val for key,val in self.user_options[user_id].items()}
            # print(user_id + str(d))
            reply_keyboard = self._recheck_user_options(
                deepcopy(list(self.user_options[user_id].values()))
            )
            resize = True
            if len(self.user_options[user_id]) > 3:
                resize = False
            markup = ReplyKeyboardMarkup(
                reply_keyboard, resize_keyboard=resize, one_time_keyboard=True
            )
        else:
            markup = ReplyKeyboardRemove()
        end = time.time()
        if self.configuration["new_user"][user_id]:
            update.message.reply_text(
                self._instruction(), parse_mode=ParseMode.MARKDOWN
            )
        update.message.reply_text(
            self.response[user_id],
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
        # record the conversation
        if self.agent[user_id].bot_recorder:
            record_data = {"Timestamp": user_utterance.get_timestamp()}
            record_data.update(self.record_data_agent[user_id])
            record_data.update({"Execution_Time": str(round(end - start, 3))})
            self.agent[user_id].bot_recorder.record_user_data(
                user_id, record_data
            )
        if self.agent[user_id].terminated_dialogue():
            print(
                f"Conversation is ending for user id = {user_id} and user name"
                f" = '{update.effective_user['first_name']}'"
            )
            del self.agent[user_id]
            feedback = (
                "Help me improve myself. Give me a feedback [here]("
                "https://forms.gle/hK9CrHu37dL89r1H6)."
            )
            feedback += (
                "\nLastly, please remember to take a note of your user id:"
                f" {user_id}"
            )
            update.message.reply_text(feedback, parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END
        else:
            return CONTINUE

    def exit(self, update, context):
        """Exit the conversation.

        Args:
            update:
            context:

        """
        user_id = str(update.effective_user["id"])
        self.response[
            user_id
        ] = "You are exiting. I hope you found a movie. Bye."
        update.message.reply_text(
            self.response[user_id],
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN,
        )
        # record the conversation
        user_id = str(update.effective_user["id"])
        print(
            f"Conversation is ending for user id = {user_id} and user name = '"
            f"{update.effective_user['first_name']}'"
        )
        if self.agent[user_id].bot_recorder:
            record_data = {
                "Timestamp": str(update.message.date),
                "User_Input": update.message.text,
                "Agent": self.response[user_id],
            }
            self.agent[user_id].bot_recorder.record_user_data(
                user_id, record_data
            )
            del self.agent[user_id]
            feedback = (
                "Help me improve myself. Give me a feedback [here]("
                "https://forms.gle/hK9CrHu37dL89r1H6)."
            )
            feedback += (
                f"\nPlease remember to take a note of your user id: {user_id}"
            )
            update.message.reply_text(feedback, parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

    def error(self, update, context):
        """Log Errors caused by Updates.

        Args:
            update:
            context:

        """
        logger.warning(
            f"Error {context.error} is caused by update {str(update)}."
        )

    def execute_agent(self, configuration):
        """Runs the conversational agent and executes the dialogue by calling
        the basic components of IAI MovieBot.

        Args:
            configuration: the settings for the agent

        """
        self.configuration = configuration
        self.configuration["new_user"] = {}
        # Get the updater and dispatcher for the telegram controller
        self.token = self.load_bot_token(self.configuration["BOT_TOKEN_PATH"])
        polling = self.configuration["POLLING"]
        if polling:
            updater = Updater(self.token, use_context=True)
            dp = updater.dispatcher
            # Add conversation handler with states START, CONTINUE_RECOMMENDATION
            # and END
            conv_handler = ConversationHandler(
                entry_points=[
                    CommandHandler("start", self.start),
                    CommandHandler("restart", self.start),
                    CommandHandler("help", self.help),
                    MessageHandler(Filters.text, self.continue_conv),
                ],
                states={
                    CONTINUE: [
                        CommandHandler("start", self.start),
                        CommandHandler("restart", self.restart),
                        CommandHandler("help", self.help),
                        CommandHandler("exit", self.exit),
                        MessageHandler(Filters.text, self.continue_conv),
                    ]
                },
                fallbacks=[CommandHandler("exit", self.exit)],
            )
            dp.add_handler(conv_handler)
            dp.add_error_handler(self.error)
            # Start the Bot
            updater.start_polling()
            # Run the controller until you press Ctrl-C or the process receives SIGINT,
            # SIGTERM or SIGABRT. This should be used most of the time, since
            # start_polling() is non-blocking and will stop the controller gracefully.
            updater.idle()
        print(
            "The components for the conversation are initialized successfully."
        )
        print("The users can access IAI MovieBot using Telegram.")

    def new_user(self, user_id):
        """Checks if the users are new or they have already conversed with the
        system before.

        Args:
            user_id: ID of the user

        Returns:
            Flag indication if users are new

        """
        file_path = "conversation_history/user_list.json"
        if not os.path.isfile(file_path):
            # create a new file with first user
            with open(file_path, "w") as user_file:
                json.dump({"users": [user_id]}, user_file, indent=4)
            return True
        if os.path.isfile(file_path):
            with open(file_path) as user_file:
                user_list = json.load(user_file)
                if user_id in user_list["users"]:
                    return False
                else:
                    user_list["users"].append(user_id)
                    with open(file_path, "w") as _user_file:
                        json.dump(user_list, _user_file, indent=4)
                    return True

    def _recheck_user_options(self, options):
        """Filters the keyboard options for a more elegant view.

        Args:
            options:

        """
        final_options = []
        row = []
        list_row = []
        last_options = []
        for option in options:
            if isinstance(option, list):
                if len(row) > 0:
                    final_options.append(deepcopy(row))
                    row = []
                if option[0] in ["/restart", "I would like to quit now"]:
                    last_options.append(option)
                    continue
                list_row.append(option[0])
                if len(list_row) >= 2:
                    final_options.append(deepcopy(list_row))
                    list_row = []
                # final_options.append(option)
            elif isinstance(option, str):
                row.append(option)
                if len(row) >= 3:
                    final_options.append(deepcopy(row))
                    row = []
        final_options.append(deepcopy(row))
        for option in last_options:
            list_row.append(option[0])
            if len(list_row) >= 2:
                final_options.append(deepcopy(list_row))
                list_row = []
        final_options.append(deepcopy(list_row))
        return final_options

    def _instruction(self, help=False):
        """Instructions for new user

        Args:
            help:  (Default value = False)

        """
        response = ""
        if not help:
            response = (
                "Hi there. I am IAI MovieBot, your movie recommending buddy. "
                "I can recommend you movies based on your preferences.\n"
                "I will ask you a few questions and based on your answers, "
                "I will try to find a movie for you.\n\n"
            )
        return (
            response
            + 'INSTRUCTIONS:\n\nTo start the conversation, issue "/start", say'
            ' Hi/Hello, or simply enter you preferences ("I want a horror'
            ' movie from the 90s").\n\nTo restart the recommendation process,'
            ' issue "/restart".\n\nTo end the conversation, issue "/exit" or'
            " say Bye/Goodbye.\n\nTo see these instructions again, issue:"
            ' "/help".'
        )  # \n\n" \
        # "You can find more details online [here](" \
        # "https://javeriahabib09.github.io/jarvis_v1.github.io/)"
