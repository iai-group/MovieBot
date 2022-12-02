from tests.mocks.mock_data_loader import MockDataLoader
import moviebot.nlu.data_loader as DL
from unittest.mock import patch


@patch("moviebot.nlu.data_loader.DataLoader", new=MockDataLoader)
def test_mock_data_loader():
    # Setup
    loader = DL.DataLoader(None, None)

    # Exercise
    result = loader.test_method()

    # Results
    truth = 123
    assert result == truth

    # Cleanup - none
