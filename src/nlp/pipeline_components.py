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


@Language.component("merge_laws")
def merge_laws(doc):
    spans = [span for span in doc.spans["spans"]]

    spans_filtered = []
    while spans:
        s = spans.pop()

        is_law_contained = False
        for other in spans_filtered:
            if (
                s.label_ == SpanType.NAVEDBA_ZAKONA.value
                and other.label_ == SpanType.NAVEDBA_ZAKONA.value
            ) and (s.start >= other.start and s.end <= other.end):
                is_law_contained = True

        if is_law_contained:
            continue

        spans_filtered.append(s)

    doc.spans["spans"] = spans_filtered
    # doc.spans["spans"].append(s)

    return doc


def _overlaps_with_margin(span1, span2, margin=150):
    return span1[0] <= span2[1] + margin and span1[1] >= span2[0] - margin


@Language.component("extract_sents_with_laws")
def extract_sents_with_laws(doc):
    extended_sentences = []
    for _sent in doc.sents:
        ents = [ent.label_ for ent in _sent.ents]
        if (EntType.CLEN.value in ents or EntType.CLEN_LEFT.value in ents) and (
            EntType.DOC_ABBR.value in ents or EntType.DOC_TITLE.value in ents
        ):
            s = Span(doc, _sent.start, _sent.end, SpanType.STAVEK_Z_ZAKONOM.value)
            doc.spans["spans"].append(s)

            TOKENS_EXTEND = 50
            start = max(_sent.start - TOKENS_EXTEND, 0)
            end = min(_sent.end + TOKENS_EXTEND, len(doc))
            extended_sentences.append((start, end))

    extended_sentences_merged = []
    while extended_sentences:
        (start, end) = extended_sentences.pop()

        for i, (other_start, other_end) in enumerate(extended_sentences_merged):
            if _overlaps_with_margin((start, end), (other_start, other_end)):
                _ = extended_sentences_merged.pop(i)

                start = min(start, other_start)
                end = max(end, other_end)
                break
        extended_sentences_merged.append((start, end))

    for start, end in extended_sentences_merged:
        s = Span(
            doc,
            start,
            end,
            SpanType.POMEMBEN_IZSEK_BESEDILA.value,
        )
        doc.spans["spans"].append(s)

    return doc
