import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer

from src.classifiers.classifier import Classifier
from src.concept import Concept
from src.passage import ConceptMention, Passage


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

    def predict(self, passage: Passage, threshold: float = 0.8) -> list[ConceptMention]:
        passage_embedding = self.embed(passage.text)
        similarity = cosine_similarity(passage_embedding, self.concept_embedding)
        if similarity > threshold:
            return [
                ConceptMention(
                    start_index=passage.start_index,
                    end_index=passage.end_index,
                    concept_id=self.concept.id,
                    text=passage.text,
                    document_id=passage.document_id,
                    zoom_level=1,
                )
            ]
        return []
