import pytest

from moviebot.nlu.data_loader import DataLoader


@pytest.fixture()
def data_loader() -> DataLoader:
    """Returns a data loader fixture."""
    return DataLoader(config={}, lemmatize_value=None)
