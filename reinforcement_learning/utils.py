"""Utility functions."""
import confuse

from usersimcrs.simulator.user_simulator import UserSimulator


def build_agenda_based_simulator(
    config: confuse.Configuration,
) -> UserSimulator:
    """Builds the agenda based user simulator.

    Args:
        config: Configuration for the simulation.

    Returns:
        Agenda based user simulator.
    """
    pass
