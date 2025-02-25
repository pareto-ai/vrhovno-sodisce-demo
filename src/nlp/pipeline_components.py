from collections import deque

from spacy.language import Language
from spacy.tokens import Span

from src.nlp.model import EntType, SpanType
from src.nlp.html_merger import HTMLMerger


@Language.factory("html_merger")
def create_html_merger(nlp, name):
    return HTMLMerger(nlp.vocab)


@Language.component("extract_laws_nastevanje")
def extract_laws_nastevanje(doc):
    """
    Searches the doc for SpanType.NAVEDBA_ZAKONA preceded by EntType.STEVNIK, for example:
        - "7. in 8. člena Zakona o pravdnem postopku"

    The algorithm will traverse from 8. člena backwards ignoring stop words
    until it finds EntType.STEVNIK. This processes repeats until it finds a non-stop word or a sentence start token.
    """
    spans = [
        span
        for span in doc.spans["spans"]
        if span.label_ == SpanType.NAVEDBA_ZAKONA.value
    ]

    queue = deque(spans)

    while queue:
        span = queue.popleft()

        start = span.start - 1
        while (
            start >= 0
            and not doc[start].is_sent_start
            and (doc[start].is_stop or doc[start].is_punct)
        ):
            start -= 1

        if start != span.start - 1 and doc[start].ent_type_ == EntType.STEVNIK.value:
            s = Span(doc, start, span.end, SpanType.NAVEDBA_ZAKONA.value)
            doc.spans["spans"].append(s)
            queue.append(s)

    return doc


@Language.component("extract_laws_closest")
def extract_laws_closest(doc):
    """
    Searches the document for lone EntType.CLEN, which have no neighboring EntType.

    DOC_ABBR and finds the closest mention to the left and to the right of the lone EntType.CLEN.
    """
    laws = [
        ent
        for ent in doc.ents
        if ent.label_ in [EntType.DOC_ABBR.value, EntType.DOC_TITLE.value]
    ]

    ents = [
        ent
        for ent in doc.ents
        if (
            ent.label_ in [EntType.CLEN.value, EntType.CLEN_LEFT.value]
            and (
                ent.start > 0
                and doc[ent.start - 1].ent_type_
                not in [EntType.DOC_ABBR.value, EntType.DOC_TITLE.value]
            )
            and (
                ent.end < len(doc) - 1
                and doc[ent.end].ent_type_
                not in [EntType.DOC_ABBR.value, EntType.DOC_TITLE.value]
            )
        )
    ]

    for ent in ents:
        left_law = sorted([law for law in laws if law.start < ent.start])
        right_law = sorted([law for law in laws if law.start >= ent.end])

        span = None
        if left_law and right_law:
            right_law = right_law[0]
            left_law = left_law[-1]

            if right_law.start - ent.end < ent.start - left_law.start:
                span = Span(
                    doc, ent.start, right_law.end, SpanType.NAVEDBA_ZAKONA_RIGHT.value
                )
            else:
                span = Span(
                    doc, left_law.start, ent.end, SpanType.NAVEDBA_ZAKONA_LEFT.value
                )
        elif left_law:
            left_law = left_law[-1]

            if not right_law:
                span = Span(
                    doc, left_law.start, ent.end, SpanType.NAVEDBA_ZAKONA_LEFT.value
                )

        elif right_law:
            right_law = right_law[0]

            if not left_law:
                span = Span(
                    doc, ent.start, right_law.end, SpanType.NAVEDBA_ZAKONA_RIGHT.value
                )

        if span:
            doc.spans["spans"].append(span)

    return doc
