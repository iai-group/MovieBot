"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using python console"""


from moviebot.agent.agent import Agent
from moviebot.controller.controller import Controller
from moviebot.core.utterance.utterance import UserUtterance


class ControllerTerminal(Controller):
    """This is the main class that controls the other components of the
    IAI MovieBot. The controller executes the conversational agent."""

    def __init__(self):
        """Initializes some basic structs for the Controller."""

    def execute_agent(self, configuration):
        """Runs the conversational agent and executes the dialogue by calling
        the basic components of IAI MovieBot

        Args:
            configuration: the settings for the agent

        """
        agent = Agent(configuration)
        agent.initialize()
        print(
            "The components for the conversation are initialized successfully."
        )
        user_options = {}
        agent_response, user_options = agent.start_dialogue()
        print(f"AGENT: {agent_response}")
        while not agent.terminated_dialogue():
            utterance = input("User: ")
            user_utterance = UserUtterance({"text": utterance})
            agent_response, user_options = agent.continue_dialogue(
                user_utterance, user_options
            )
            print(f"AGENT: {agent_response}")
            if user_options:
                print(list(user_options.values()))
        agent.end_dialogue()
