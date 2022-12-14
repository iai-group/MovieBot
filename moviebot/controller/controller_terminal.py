"""This file contains the Controller class which controls the flow of the
conversation while the user interacts with the agent using python console.
"""

import questionary

from moviebot.controller.controller import Controller
from moviebot.core.shared.utterance.utterance import UserUtterance


class ControllerTerminal(Controller):
    """This is the main class that controls the other components of the
    IAI MovieBot. The controller executes the conversational agent."""

    def execute_agent(self) -> None:
        """Runs the conversational agent and executes the dialogue."""
        agent = None
        while True:
            if not agent or self.restart(user_utterance):
                agent = self.initialize_agent()
                agent_response, user_options = agent.start_dialogue()
            else:
                agent_response, user_options = agent.continue_dialogue(
                    user_utterance, user_options
                )

            agent_prompt = f"AGENT: {agent_response}\n"
            if agent.terminated_dialogue():
                questionary.print(f" {agent_prompt}", style="bold")
                break

            user_prompt = "USER: "
            if not user_options:
                answer = questionary.text(
                    f"{agent_prompt} {user_prompt}",
                    qmark="",
                ).ask()
            else:
                options = [item[0] for item in user_options.values()]
                formatted_options = "\n     ".join(options)
                answer = questionary.autocomplete(
                    f"{agent_prompt}     {formatted_options}\n {user_prompt}",
                    qmark="",
                    choices=options,
                ).ask()

            user_utterance = UserUtterance({"text": answer})

        agent.end_dialogue()
