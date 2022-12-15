"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using python console.
"""


from moviebot.controller.controller import Controller
from moviebot.core.utterance.utterance import UserUtterance


class ControllerTerminal(Controller):
    """This is the main class that controls the other components of the
    IAI MovieBot. The controller executes the conversational agent."""

    def execute_agent(self) -> None:
        """Runs the conversational agent and executes the dialogue."""
        agent = None
        while True:
            utterance = input("User: ")
            user_utterance = UserUtterance({"text": utterance})

            if not agent or self.restart(user_utterance):
                agent = self.initialize_agent()
                agent_response, user_options = agent.start_dialogue()
            else:
                agent_response, user_options = agent.continue_dialogue(
                    user_utterance, user_options
                )

            print(f"AGENT: {agent_response}")
            if user_options:
                print(list(user_options.values()))

            if agent.terminated_dialogue():
                break

        agent.end_dialogue()
