import sys
import os
import json
import time
from copy import deepcopy
from collections import defaultdict

from run_bot import arg_parse
from moviebot.agent.agent import Agent
from moviebot.utterance.utterance import UserUtterance


def get_data_path(filename):
    return os.path.join(os.getcwd(), 'eval', 'data', filename)


def load_json(filename):
    """Load contents of a json file.
    """
    try:
        with open(get_data_path(filename), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f'File \'{filename}\' not found.')
        return None


def save_json(data, filename):
    """Save contents of data to json file.
    """
    with open(get_data_path(filename), '+w') as f:
        json.dump(data, f)


def load_config(filename=None):
    """Load config from file using same parser as moviebot.

    Args:
        filename (Text, optional): path to config. Defaults to None.

    Returns:
        dict: Dictionary loaded from config file.
    """
    args = ['', '']
    if filename:
        args.append(filename)
    return arg_parse(args)[0]


def parse_ccpem_collection(collection):
    """Parse CCPEM collection.

    Args:
        conversations (List(dict)): collection of conversations.

    Returns:
        List[Dict]: Text and segments parts of the collection.
    """
    return [[{
        'text': utterance['text'],
        'segments': utterance.get('segments', [])
    }
             for utterance in conversation['utterances']]
            for conversation in collection]


def get_conversations(collection):
    """Get only utterances grouped by conversation.

    Args:
        collection (List(dict)): collection of conversations.

    Returns:
        List[List]: List of utterances in a list of conversations
    """
    return [[utterance['text']
             for utterance in conversation]
            for conversation in collection]


def get_segments(collection, annotationTypes=None):
    """Given annotation types return all semantic annotations of that type for
    all utterances.

    Args:
        collection (List(dict)): List of conversations.
        annotationTypes (dict, optional): Dictionary with annotation tye -
        entity type pairs. Defaults to None.

    Returns:
        List(dict): Collection with annotations equal to annotation types.
    """
    segments = []
    for conversation in collection:
        conversation_segment = []
        for utterance in conversation:
            if not annotationTypes:
                conversation_segment.append(utterance['segments'])
                continue

            segments_to_keep = []
            for segment in utterance['segments']:
                annotations = [
                    ann for ann in segment['annotations']
                    if ann['entityType'] in annotationTypes.get(
                        ann['annotationType'], [])
                ]

                if len(annotations) > 0:
                    to_keep = deepcopy(segment)
                    to_keep['annotations'] = annotations
                    segments_to_keep.append(to_keep)
            conversation_segment.append(segments_to_keep)
        segments.append(conversation_segment)
    return segments


def get_annotation_types(collection):
    """Get all annotation types that exist in the evaluation set.

    Args:
        collection (List(Dict)): Collection of conversations.

    Returns:
        Dict: All annotation types.
    """
    annotation_types = defaultdict(set)
    for utterance in collection:
        for segment in utterance['segments']:
            for annotation in segment['annotations']:
                annotation_types[annotation['annotationType']].add(
                    annotation['entityType'])

    return annotation_types


def get_slot_annotator(config):
    """Load an agent with a given config.

    Args:
        config (Dict): Contents of a configuration file.

    Returns:
        SlotAnnotator: Returns instance of SlotAnnotator.
    """
    agent = Agent(config)
    agent.initialize()
    return agent.nlu.intents_checker.slot_annotator


def annotate_slot_utterance(annotator, slot, utterance):
    """Annotates single utterance for single slot.

    Args:
        annotator (SlotAnnotator): Annotator used for annotation.
        slot (Slots): Slot for which to annotate.
        utterance (Text): Raw text for which to annotate.

    Returns:
        List[Dict]: List of semantic annotations for utterance.
    """
    user_utterance = UserUtterance({'text': utterance})
    constraints = annotator.slot_annotation(slot, user_utterance) or []
    semantic_annotations = [
        annotation for constraint in constraints
        for annotation in constraint.annotation
    ]
    return [
        remove_non_seriasable(annotation.__dict__)
        for annotation in remove_duplicates(semantic_annotations)
    ]


def remove_non_seriasable(d):
    """ Converts AnnotationType and EntityType classes to string
    """
    return {
        k: str(val.name).lower() if k in ('annotation_type',
                                          'entity_type') else val
        for k, val in d.items()
    }


def annotate_conversation_for_slot(annotator, slot, conversation, i=-1):
    """Annotates conversation for a single slot.

    Args:
        annotator (SlotAnnotator): Annotator used for annotation.
        slot (Slots): Slot for which to annotate.
        conversation (List[Text]): List of utterances.

    Returns:
        List[List[Dict]]: List of semantic annotations for conversation.
    """
    if i >= 0:
        print(f'Annotating conversation {i} for slot \'{slot}\'')
    return [
        annotate_slot_utterance(annotator, slot, utterance)
        for utterance in conversation
    ]


def remove_duplicates(annotations):
    """Remove duplicate annotations. This is mostly used for persons when same
    person can be both actor and director.

    Args:
        annotations (List): List of annotations.

    Returns:
        List: List of annotations without duplicates.
    """
    return [
        annotation for i, annotation in enumerate(annotations)
        if not any(annotation == ann for ann in annotations[i + 1:])
    ]


def overlaps(annotation, truth):
    """Check whether two annotations overlap.
    """
    return (annotation['start'] <= truth['startIndex']
            and annotation['end'] > truth['startIndex']) or (
                truth['startIndex'] <= annotation['start']
                and truth['endIndex'] > annotation['start'])


def get_matches(annotations, true_annotations):
    """Get all overlapping entities. Since we are evaluation on slot bases,
    they will be annotated as same entity.

    Args:
        annotations (List): List of annotations.
        true_annotations (List): List of ground truth annotations.

    Returns:
        int: Number of matching annotations.
    """
    return sum(
        overlaps(annotation, truth)
        for annotation in annotations
        for truth in true_annotations)


def evaluate(conversations, truth_segments):
    """Main evaluation function. Requires annotated conversations and ground
    truth annotations. Calculates micro precision, micro recall and f1 scores.

    Args:
        conversations (List[List[Dict]]): List of annotated conversations.
        truth_segments (List[List[Dict]]): List of Lists of true annotations.

    Returns:
        (float, float, float): Precision, Recall and f1 scores
    """
    total_num_annotations = 0
    total_num_truth = 0
    total_matches = 0
    all_annotation_pairs = [
        annotation_pairs
        for conversation_pairs in zip(conversations, truth_segments)
        for annotation_pairs in zip(*conversation_pairs)
    ]
    for _, (annotation, true_annotation) in enumerate(all_annotation_pairs):
        total_matches += get_matches(annotation, true_annotation)

        total_num_annotations += len(annotation)
        total_num_truth += sum(
            len(ann['annotations']) for ann in true_annotation)

    p_micro = total_matches / total_num_annotations if total_num_annotations else 0
    r_micro = total_matches / total_num_truth if total_num_truth else 0
    f1 = 2 * p_micro * r_micro / (p_micro + r_micro)
    return p_micro, r_micro, f1


def get_annotations(slots, entity_types, force=False):
    """Checks whether annotation file exists, else runs annotations for all
    slots for the entire collection.

    Args:
        force (bool, optional): Force re-annotating the collection. Defaults to
            False.

    Returns:
        Dict: Dictionary with annotatins and durations for each slot.
    """
    filename = 'annotations.json'
    if not force:
        annotations = load_json(filename)
        if annotations:
            return annotations

    print('Creating new annotation file...')
    raw_data = load_json('data.json')
    data = parse_ccpem_collection(raw_data)
    conversations = get_conversations(data)

    conf = load_config()
    annotator = get_slot_annotator(conf)

    results = defaultdict(dict)
    for slot, entity_type in zip(slots, entity_types):
        segments = get_segments(data, {'ENTITY_NAME': [entity_type]})
        start = time.time()
        annotations = [
            annotate_conversation_for_slot(annotator, slot, utterances, i)
            for i, utterances in enumerate(conversations)
        ]
        results[slot]['duration'] = time.time() - start
        results[slot]['annotations'] = annotations
        results[slot]['metrics'] = evaluate(annotations, segments)

    save_json(results, filename)
    return results


if __name__ == '__main__':
    slots = ['genres', 'actors', 'title']
    entity_types = ['MOVIE_GENRE_OR_CATEGORY', 'PERSON', 'MOVIE_OR_SERIES']

    res = get_annotations(slots, entity_types)

    for slot in slots:
        p, r, f1 = res[slot]['metrics']
        print(f'\nScores for {slot}: \n')
        print(f'\tPrecision (micro-averaged): {round(p, 5)}')
        print(f'\tRecall (micro-averaged): {round(r, 5)}')
        print(f'\tF1: {round(f1, 5)}')
        print(f'\nAnnotation took {round(res[slot]["duration"]/60, 3)} minutes')
