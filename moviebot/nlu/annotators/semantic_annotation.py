from abc import ABC, abstractmethod


class SemanticAnnotation(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def annotate(self, utterance):


