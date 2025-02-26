from pathlib import Path

import pandas as pd
from spacy.tokens import Span

from src.nlp import spacy_classla
from src.nlp.patterns import ENTITY_PATTERNS, SPAN_PATTERNS, EntType
from src.nlp.pipeline_components import *


class TextProcessor:
    def __init__(
        self,
        mappings_path: Path = None,
    ) -> None:
        self.mappings_path = mappings_path

        self.initialize_nlp_pipeline()

    def initialize_nlp_pipeline(self):
        self.nlp = spacy_classla.load_pipeline(
            "sl",
            processors="tokenize,pos,lemma",
        )

        if self.mappings_path:
            self.lemmatized_laws = pd.read_parquet(self.mappings_path)
            self.lemmatized_laws = self.lemmatized_laws.fillna("")
        else:
            self.lemmatized_laws = None

        self.init_entity_ruler()
        self.init_span_ruler()

    def init_entity_ruler(self):
        """Initializes Entity Ruler with the entity ruler patterns."""

        self.nlp.add_pipe("sentencizer")
        ruler = self.nlp.add_pipe("entity_ruler")

        if self.lemmatized_laws is not None:
            # First add doc abbreviations
            abbr_patterns = []

            for abbr in self.lemmatized_laws["abbreviation"].unique():
                if not abbr:
                    continue

                # Create a literal match pattern but also take care of - in words
                # as tokenizer might split the words apart.
                if len(abbr) > 2 and abbr.lower() not in ["ter"]:
                    # Take care of
                    if "-" in abbr:
                        splits = abbr.split("-")
                        pattern = []
                        for i, word in enumerate(splits):
                            pattern.append({"LOWER": word.lower()})
                            if i < len(splits) - 1:
                                pattern.append({"ORTH": "-", "OP": "?"})

                        abbr_patterns.append(
                            {
                                "label": EntType.DOC_ABBR.value,
                                "pattern": pattern,
                            }
                        )

                    abbr_patterns.append(
                        {
                            "label": EntType.DOC_ABBR.value,
                            "pattern": [({"LOWER": abbr.lower()})],
                        }
                    )
                elif abbr:
                    # abbreviations with len <= 2  should always match capital case
                    # due to vocab collision
                    abbr_patterns.append(
                        {
                            "label": EntType.DOC_ABBR.value,
                            "pattern": [{"ORTH": abbr}],
                        }
                    )
                    abbr_patterns.append(
                        {
                            "label": EntType.DOC_ABBR.value,
                            "pattern": [{"ORTH": abbr + "."}],
                        }
                    )

            # Second, add document title patterns
            title_patterns = self.get_entity_ruler_title_patterns(
                [
                    x
                    for x in self.lemmatized_laws["document_title_lemmatized"].to_list()
                    if x
                ]
            )

        patterns = (
            [ENTITY_PATTERNS, abbr_patterns, title_patterns]
            if self.lemmatized_laws is not None
            else [ENTITY_PATTERNS]
        )

        for pattern in patterns:
            ruler.add_patterns(pattern)

    def init_span_ruler(self):
        Span.set_extension(
            "normalized_law",
            getter=lambda span: self.get_normalized_law(
                span,
                possibilities_titles=self.lemmatized_laws[
                    "document_title_lemmatized"
                ].to_list(),
                possibilities_abbr=self.lemmatized_laws["abbreviation"].to_list(),
            ),
            force=True,
        )

        self.nlp.add_pipe("html_merger")
        self.nlp.add_pipe("merge_entities")

        span_ruler = self.nlp.add_pipe(
            "span_ruler", config={"spans_key": "spans", "validate": True}
        )
        span_ruler.add_patterns(SPAN_PATTERNS)

        # # Add post-processing components
        self.nlp.add_pipe("extract_laws_nastevanje")
        # self.nlp.add_pipe("extract_laws_closest")

    def get_entity_ruler_title_patterns(self, lemmatized_titles):
        """Get Document title patterns from the lemmatized version."""

        def document_title_lemma_pattern(lemma):
            if lemma in [",", ".", "-", ":", "/"]:
                return {"LEMMA": lemma, "OP": "?"}
            else:
                return {"LEMMA": lemma}

        title_patterns = []
        for lemmatized_title in lemmatized_titles:
            pattern = [
                document_title_lemma_pattern(lemma)
                for lemma in lemmatized_title.split()
            ]
            title_patterns.append(
                {"label": EntType.DOC_TITLE.value, "pattern": pattern}
            )

        return title_patterns

    def lemmatize_text(self, text):
        try:
            text = str(text).strip()
            if not text or text.isspace():
                return ""

            q = self.nlp(text)
            result = " ".join([x.lemma_ for x in q])

            return result

        except Exception as e:
            print(f"Error processing text: '{text}'")
            print(f"Error details: {str(e)}")
            raise
