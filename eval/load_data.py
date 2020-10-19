#%%
import json
import os

_path = os.getcwd()


def load_json(filename):
    path = os.path.join(_path, 'data', filename)
    with open(path, 'r') as f:
        data = json.load(f)

    return data


def save_json(data, filename):
    path = os.path.join(_path, 'data', filename)
    with open(path, '+w') as f:
        json.dump(data, f)


def parse_CCPEM_collection(conversations):
    data = {
        speaker: {
            'texts': [],
            'segments': [],
        } for speaker in ['ASSISTANT', 'USER']
    }

    for conversation in conversations:
        for utterance in conversation['utterances']:
            data[utterance['speaker']]['texts'].append(utterance['text'])
            data[utterance['speaker']]['segments'].append(
                utterance['segments'] if 'segments' in utterance else {})

    return data


if __name__ == '__main__':
    data = load_json('data.json')
    data = parse_CCPEM_collection(data)

# %%
