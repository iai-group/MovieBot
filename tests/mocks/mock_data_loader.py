tag_words = {
    "user_reveal": "",
    "user_inquire": "",
    "user_reveal_inquire": "",
}

slot_values = {
    "actors": {},
    "directors": {},
}


class MockDataLoader:
    def __init__(self, config, _lemmatize_value):
        pass

    def load_database(self):
        return slot_values

    def load_tag_words(self, a=None):
        return tag_words

    def test_method(self):
        return 123
