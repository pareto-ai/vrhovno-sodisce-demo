import re
from pathlib import Path

import pymupdf
import textract

ABBR_PATTERN = r"\((.*?)\)"


def _get_law_abbreviation(title, abbr_pattern=ABBR_PATTERN):
    abbreviation = re.findall(abbr_pattern, title)
    abbreviation = [x if not x.split(",") else x.split(",")[0] for x in abbreviation]
    abbreviation = [x for x in abbreviation if len(x.split(" ")) < 2]
    abbreviation = [x for x in abbreviation if not x.islower()]

    if abbreviation:
        return abbreviation[-1].strip()  # .split("-")[0]
    return ""


def _strip_law_abbreviation(text, abbr_pattern=ABBR_PATTERN):
    return re.sub(abbr_pattern, "", text).strip()


def _find_entity(doc, entity_name):
    return list(filter(lambda ent: ent.label_ == entity_name, doc.ents))


def _normalize_input_for_clen(clen):
    split = clen.split(" ")
    for sub in split:
        if any([x.isdigit() for x in sub]):
            if "." not in sub:
                return f"{sub}. člen".lower()
            return f"{sub} člen".lower()
    return clen


def _map_titles_to_abbreviations(titles, tp):
    mappings = tp.lemmatized_laws

    abbrs = []
    for x in titles:
        lemmatized_title = tp.lemmatize_text(x)
        _abbrs = (
            mappings.loc[
                mappings["document_title_lemmatized"] == lemmatized_title,
                "abbreviation",
            ]
            .drop_duplicates()
            .to_list()
        )
        abbrs.extend(_abbrs)
    return [x for x in abbrs if x]


def pdf_to_text(file_path: Path):
    # pymupdf, fall back to OCR if now sucessfull
    doc = pymupdf.open(file_path)

    pages = [page.get_text() for page in doc]
    pages = [p for p in pages if p]
    text = " ".join(pages)

    if not text:
        text = textract.process(file_path, extension="pdf", method="tesseract")

    return text
