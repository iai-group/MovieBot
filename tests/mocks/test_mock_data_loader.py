from unittest.mock import patch

import moviebot.nlu.data_loader as DL
from tests.mocks.mock_data_loader import MockDataLoader


@patch("moviebot.nlu.data_loader.DataLoader", new=MockDataLoader)
def test_mock_data_loader():
    loader = DL.DataLoader(None, None)
    result = loader.test_method()
    truth = 123
    assert result == truth
