tag_words = {
    "user_reveal": "",
    "user_inquire": "",
    "user_reveal_inquire": "",
}

slot_values = {
    "actors": {
        "Tom Hanks": "tom hank",
        "Tim Allen": "tim allen",
        "Don Rickles": "don rickles",
    },
    "directors": {
        "John Lasseter": "john lasseter",
        "Joe Johnston": "joe johnston",
        "Howard Deutch": "howard deutch",
    },
}


class MockDataLoader:
    def __init__(self, config, _lemmatize_value):
        pass

    def load_slot_value_pairs(self):
        return slot_values

    def load_tag_words(self, file_path=None):
        return tag_words

    def test_method(self):
        return 123
