import random
from typing import List

import spacy
from spacy.training import Example
from spacy.util import minibatch

from src.classifiers.classifier import Classifier
from src.concept import Concept
from src.document import Document


class SpanCatClassifier(Classifier):
    """
    Classifier that uses spaCy's SpanCategorizer model to find spans in text.
    """

    def __init__(self, concepts: List[Concept], model_name: str = "en_core_web_sm"):
        self.concepts = concepts
        self.nlp = spacy.load(model_name)

        if "spancat" not in self.nlp.pipe_names:
            self.nlp.add_pipe("spancat")
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "spancat"]
        self.nlp.disable_pipes(other_pipes)

        self.spancat = self.nlp.get_pipe("spancat")
        self.spancat.add_label(self.concept.preferred_label)

    def __repr__(self):
        concept_labels = ",".join(
            [concept.preferred_label for concept in self.concepts]
        )
        return f"{self.__class__.__name__}({concept_labels})"

    def _generate_training_data(self, documents: List[Document]) -> List[Example]:
        """
        Generate training data in spaCy format from a list of documents.

        :param List[Document] documents: A list of training documents including concept
        spans
        :return List[Example]: A list of training examples in spaCy format
        """
        examples = []
        for document in documents:
            doc = self.nlp.make_doc(document.text)
            example = Example.from_dict(doc, document.to_dict())
            examples.append(example)
        return examples

    def _train(
        self, examples: List[Example], epochs: int = 10, batch_size: int = 8
    ) -> "SpanCatClassifier":
        """
        Train the SpanCat model on the training data.

        :param List[Example] examples: A list of training examples in spaCy format
        :param int epochs: The number of training epochs
        :param int batch_size: The number of examples in each training batch
        :return SpanCatClassifier: The trained classifier
        """
        for _ in range(epochs):
            random.shuffle(examples)
            for batch in minibatch(examples, size=batch_size):
                self.nlp.update(batch, drop=0.5, losses={})
        return self

    def fit(self, documents: List[Document]) -> "SpanCatClassifier":
        """
        Fit the classifier to the training data.

        :param List[Document] documents: A list of training documents including concept
        spans
        :return SpanCatClassifier: The trained classifier
        """
        training_data = self._generate_training_data(documents)
        self._train(training_data)
        return self
