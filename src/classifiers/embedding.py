from typing import List

import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer

from src.classifiers.classifier import Classifier
from src.concept import Concept
from src.document import Document
from src.span import Span


class EmbeddingClassifier(Classifier):
    """Uses embeddings to find spans of text which match the given concept."""

    def __init__(
        self,
        concept: Concept,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
    ):
        super().__init__(concept)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

        # take the mean of the embeddings for all of the concept's labels
        label_embeddings = [self.embed(label) for label in concept.all_labels]
        self.concept_embedding = torch.stack(label_embeddings).mean(dim=0)

    def embed(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1)

    def predict(self, document: Document, threshold=0.8) -> List[Span]:
        spans = []
        for span in document.sentence_spans:
            text = document.text[span.start_index : span.end_index]
            span_embedding = self.embed(text)
            similarity = cosine_similarity(span_embedding, self.concept_embedding)
            if similarity > threshold:
                spans.append(span)
        return spans
