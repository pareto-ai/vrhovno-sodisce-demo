from spacy.tokens import Token
from spacy.matcher import Matcher
from spacy.util import filter_spans


class HTMLMerger:
    """A NLP pipeline component that finds and groups <br>, <p> HTML tags, which are
    used for defining the paragraphs.
    """

    def __init__(self, vocab):
        patterns = [
            [{"ORTH": "<"}, {"LOWER": "br"}, {"ORTH": ">"}],
            [
                {"ORTH": "<"},
                {"LOWER": "br"},
                {"ORTH": "/"},
                {"ORTH": ">"},
                {"ORTH": "<"},
                {"LOWER": "br"},
                {"ORTH": "/"},
                {"ORTH": ">"},
            ],
            [
                {"ORTH": "<"},
                {"LOWER": "br"},
                {"ORTH": "/"},
                {"ORTH": ">"},
            ],
            [
                {"ORTH": "<"},
                {"ORTH": "/"},
                {"LOWER": "p"},
                {"ORTH": ">"},
                # {"ORTH": "<"},
                # {"LOWER": "p"},
                # {"TEXT": {"REGEX": r"[^>]"}, "OP": "*"},
                # {"ORTH": ">"},
            ],
        ]
        Token.set_extension("html_break", default=False, force=True)
        Token.set_extension("paragraph_start", default=False, force=True)
        self.matcher = Matcher(vocab)
        self.matcher.add("HTML_BREAK", patterns)

    def __call__(self, doc):
        """Called by the pipeline.

        Args:
            doc: modified doc.
        """
        spans = self.matcher(doc, as_spans=True)
        spans = filter_spans(spans)

        with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)
                for token in span:
                    token._.html_break = True
                    if token.i < len(doc) - 1:
                        doc[token.i + 1]._.paragraph_start = True

            # Mark the first token as a start of paragraph
            if len(doc) > 0:
                doc[0]._.paragraph_start = True
                # doc[len(doc) - 1]._.paragraph_start = True
        return doc
