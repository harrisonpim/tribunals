from src.classifiers.classifier import Classifier
from src.classifiers.elasticsearch import ElasticsearchClassifier
from src.classifiers.embedding import EmbeddingClassifier
from src.classifiers.regex import RegexClassifier
from src.classifiers.setfit import SetFitClassifier
from src.classifiers.spancat import SpanCatClassifier
from src.concept import Concept

__all__ = [
    "Classifier",
    "ElasticsearchClassifier",
    "EmbeddingClassifier",
    "RegexClassifier",
    "SetFitClassifier",
    "SpanCatClassifier",
]


class ClassifierFactory:
    @staticmethod
    def create(concept: Concept) -> Classifier:
        """
        Create a classifier for a concept, whose level of sophistication is based on
        the available data.

        The factory will create a SetFitClassifier if labelled examples are available,
        an EmbeddingClassifier if there are a large number of labels, and a
        RegexClassifier otherwise. NB other classifiers (listed above) exist, and can
        be added to the factory as needed.

        :param Concept concept: The concept to classify, with variable amounts of data
        :return BaseClassifier: The classifier for the concept, trained where applicable
        """
        if concept.examples:
            model = SetFitClassifier(concept)
            model.fit()
        elif len(concept.all_labels) > 5:
            model = EmbeddingClassifier(concept)
        else:
            model = RegexClassifier(concept)

        return model
