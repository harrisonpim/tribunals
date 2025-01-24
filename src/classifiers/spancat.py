import random

import spacy
from spacy.tokens import Span as SpacySpan
from spacy.training import Example
from spacy.util import minibatch

from src.classifiers.classifier import Classifier
from src.concept import Concept
from src.passage import ConceptMention, Passage
from src.passage_group import PassageGroup


class SpanCatClassifier(Classifier):
    """
    Classifier that uses spaCy's SpanCategorizer model to find spans in text.
    """

    def __init__(self, concept: Concept, model_name: str = "en_core_web_sm"):
        super().__init__(concept)
        self.nlp = spacy.load(model_name)

        if "spancat" not in self.nlp.pipe_names:
            self.nlp.add_pipe("spancat")
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "spancat"]
        self.nlp.disable_pipes(other_pipes)

        self.spancat = self.nlp.get_pipe("spancat")
        self.spancat.add_label(self.concept.preferred_label)

    def _generate_training_data(self, passage_group: PassageGroup) -> list[Example]:
        """
        Generate training data in spaCy format from a passage group.

        :param PassageGroup passage_group: A passage group containing training examples
        :return list[Example]: A list of training examples in spaCy format
        """
        examples = []
        for passage in passage_group.passages:
            doc = self.nlp.make_doc(passage.text)
            example = Example.from_dict(doc, passage.model_dump())
            examples.append(example)
        return examples

    def _train(
        self, examples: list[Example], epochs: int = 10, batch_size: int = 8
    ) -> None:
        """
        Train the SpanCat model on the training data.

        :param list[Example] examples: A list of training examples in spaCy format
        :param int epochs: The number of training epochs
        :param int batch_size: The number of examples in each training batch
        """
        for _ in range(epochs):
            random.shuffle(examples)
            for batch in minibatch(examples, size=batch_size):
                self.nlp.update(batch, drop=0.5, losses={})

    def fit(self, passage_group: PassageGroup) -> "SpanCatClassifier":
        """
        Fit the classifier to the training data.

        :param PassageGroup passage_group: A passage group containing training examples
        :return SpanCatClassifier: The trained classifier
        """
        training_data = self._generate_training_data(passage_group)
        self._train(training_data)
        return self

    def predict(self, passage: Passage) -> list[ConceptMention]:
        """
        Predict spans which match the concept in the passage text.

        :param Passage passage: The passage to classify
        :return list[ConceptMention]: A list of concept mentions in the passage
        """
        doc = self.nlp(passage.text)
        mentions = []
        found_spans: list[SpacySpan] = doc.spans["sc"]
        for span in found_spans:
            mentions.append(
                ConceptMention(
                    start_index=span.start,
                    end_index=span.end,
                    concept_id=self.concept.id,
                    text=span.text,
                    document_id=passage.document_id,
                    zoom_level=1,
                )
            )
        return mentions
