#%%
import json
import os, sys
from collections import defaultdict
from copy import deepcopy
import nltk
import time

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

os.chdir('c:/users/ivicauis/documents/uni/dat620/moviebot')
_path = os.getcwd()

from run_bot import arg_parse
# from moviebot.nlu.rule_based_annotator import RBAnnotator
from moviebot.agent.agent import Agent
# from moviebot.dialogue_manager.slots import Slots


def load_json(filename):
    path = os.path.join(_path, 'eval', 'data', filename)
    with open(path, 'r') as f:
        data = json.load(f)

    return data


def save_json(data, filename):
    path = os.path.join(_path, 'eval', 'data', filename)
    with open(path, '+w') as f:
        json.dump(data, f)


def load_config(filename=None):
    args = [None, None]
    if filename:
        args.append(filename)
    return arg_parse(args)[0]


def parse_CCPEM_collection(conversations):
    utterances = []

    for conversation in conversations:
        for utterance in conversation['utterances']:
            utterances.append({
                'text': utterance['text'],
                'segments': utterance.get('segments', [])
            })

    return utterances


def get_utterances(collection):
    return [utterance['text'] for utterance in collection]


def get_segments(collection, annotationTypes=None):
    segments = []
    for utterance in collection:
        if not annotationTypes:
            segments.append(utterance['segments'])
            continue

        segments_to_keep = []
        for segment in utterance['segments']:
            annotations = []
            for ann in segment['annotations']:
                if ann['annotationType'] in annotationTypes and ann[
                        'entityType'] in annotationTypes[ann['annotationType']]:
                    annotations.append(ann)

            if len(annotations) > 0:
                to_keep = deepcopy(segment)
                to_keep['annotations'] = annotations
                segments_to_keep.append(to_keep)
        segments.append(segments_to_keep)

    return segments


def get_annotation_types(collection):
    annotation_types = defaultdict(set)
    for utterance in collection:
        for segment in utterance['segments']:
            for annotation in segment['annotations']:
                # if ann['annotationType'] == 'ENTITY_NAME' and ann[
                #         'entityType'] == 'SOMETHING_ELSE':
                #     print(annotation['text'])
                annotation_types[annotation['annotationType']].add(
                    annotation['entityType'])

    return annotation_types


def get_slot_annotator(config):
    agent = Agent(config)
    agent.initialize()
    return agent.nlu.intents_checker.slot_annotator


def annotate_single_slot_utterance(annotator, slot, text):
    processed_text = annotator._lemmatize_value(text)
    #print(processed_text)
    item_constraints = annotator.slot_annotation(slot, processed_text, text)
    return item_constraints if item_constraints else []


def parse_annotations(annotations):
    return [str(annotation) for annotation in annotations]


def annotate_all_slots(annotator, slots, text):
    annotations = []
    for slot in slots:
        annotations.append(annotate_single_slot_utterance(
            annotator, slot, text))
    return annotations


def annotate_texts_for_slot(annotator, slot, texts):
    annotations = []
    for i, text in enumerate(texts):
        if i % (len(texts) // 100) == 0:
            print(
                f'{round(i / (len(texts)//100), 2)}% done annotating for slot {slot}'
            )
        annotations.append(annotate_single_slot_utterance(
            annotator, slot, text))
    return annotations


def evaluate_texts(annotations, gold_truth):
    total_num_annotations = 0
    total_num_truth = 0
    total_matches = 0
    for i, b in enumerate(zip(annotations, gold_truth)):
        annotation, true_annotation = b
        annotation = remove_duplicate_persons(annotation)

        # current_matches = total_matches
        # current_truth = total_num_truth
        # current_ann = total_num_annotations

        total_matches += sum([
            get_similarity(ann, truth)
            for truth in true_annotation
            for ann in annotation
        ])
        total_num_annotations += len(annotation)
        total_num_truth += sum(
            len(ann['annotations']) for ann in true_annotation)

        # if total_num_annotations - current_ann != total_matches - current_matches:
        #     print(parse_annotations(annotation))
        #     print(true_annotation)
        #     print(i)
        #     return

    P_micro = total_matches / total_num_annotations if total_num_annotations else 0
    R_micro = total_matches / total_num_truth if total_num_truth else 0
    F1 = 2 * P_micro * R_micro / (P_micro + R_micro)
    return P_micro, R_micro, F1


def get_similarity(tag, truth, treshold=0.5):
    entity_types = [
        annotation['entityType'] for annotation in truth['annotations']
    ]
    entity_match = False
    if tag.slot == 'genres' and 'MOVIE_GENRE_OR_CATEGORY' in entity_types:
        entity_match = True
    if tag.slot == 'title' and 'MOVIE_OR_SERIES' in entity_types:
        entity_match = True
    if tag.slot in ['actors', 'directors'] and 'PERSON' in entity_types:
        entity_match = True
    if entity_match:
        vectorizer = CountVectorizer(analyzer='char_wb', ngram_range=(2, 2))
        X = vectorizer.fit_transform([tag.value, truth['text'].lower()])
        a, b = X.toarray()
        if cosine_similarity([a], [b])[0][0] < treshold:
            print(tag.value, truth['text'].lower())
        return cosine_similarity([a], [b])[0][0] > treshold

        # return (1 - nltk.edit_distance(tag.value, truth['text']) /
        #         len(truth['text'])) > treshold
    else:
        return 0


def remove_duplicate_persons(annotations):
    actors = [
        annotation.value
        for annotation in annotations
        if annotation.slot == 'actors'
    ]
    if not actors:
        return annotations

    marked_for_removal = []
    for annotation in annotations:
        if annotation.slot == 'director' and annotation.value in actors:
            marked_for_removal.append(annotation)

    for duplicate in marked_for_removal:
        annotations.remove(duplicate)

    return annotations


# %%
if __name__ == '__main__':
    raw_data = load_json('data.json')
    data = parse_CCPEM_collection(raw_data)
    utterances = get_utterances(data)

    conf = load_config()
    annotator = get_slot_annotator(conf)

    slots = ['genres', 'actors', 'title']  #'keywords']
    entity_types = ['MOVIE_GENRE_OR_CATEGORY', 'PERSON', 'MOVIE_OR_SERIES']

    # Test for genres
    for slot, entity_type in zip(slots, entity_types):
        start = time.time()
        annotations = annotate_texts_for_slot(annotator, slot,
                                              utterances[:1000])
        duration = time.time() - start

        segments = get_segments(data, {'ENTITY_NAME': [entity_type]})

        p, r, f1 = evaluate_texts(annotations, segments)

        with open(os.path.join(_path, 'eval', 'results.txt'), 'a+') as f:
            print(f'\nScores for {slot}: \n', file=f)
            print(f'\tPrecision (micro-averaged): {round(p, 5)}', file=f)
            print(f'\tRecall (micro-averaged): {round(r, 5)}', file=f)
            print(f'\tF1: {round(f1, 5)}', file=f)
            print(f'\nAnnotation took {round(duration/60, 3)} minutes', file=f)
# %%
