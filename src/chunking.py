import spacy

from src.passage import Parent, Passage, Sentence, TransformationEvent


def join_passages(passage_group: list[Passage]) -> Passage:
    document_id = (
        passage_group[0].document_id
        if len(set([p.document_id for p in passage_group])) == 1
        else None
    )
    transformation_event = TransformationEvent(
        event_type=join_passages.__name__,
        parents=[
            Parent(
                type=passage.name,
                id=passage.id,
                start_index=0,
                end_index=len(passage.text),
            )
            for passage in passage_group
        ],
    )
    return Passage(
        text=" ".join([p.text for p in passage_group]),
        document_id=document_id,
        transformation_history=[transformation_event],
    )


def split_text_into_sentences(passage: Passage) -> list[Sentence]:
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    analysed_passage = nlp(passage.text)
    sentences = []
    for sent in analysed_passage.sents:
        transformation_event = TransformationEvent(
            event_type=split_text_into_sentences.__name__,
            parents=[
                Parent(
                    type=passage.name,
                    id=passage.id,
                    start_index=sent.start_char,
                    end_index=sent.end_char,
                )
            ],
        )

        sentence = Sentence(
            text=sent.text,
            transformation_history=passage.transformation_history
            + [transformation_event],
        )
        sentences.append(sentence)

    return sentences
