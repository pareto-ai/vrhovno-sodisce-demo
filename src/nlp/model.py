from enum import Enum


class ClenCombinations(str, Enum):
    CLEN = "clen"
    CLEN_ABBREVIATED = "cl"
    CLEN_ABBREVIATED_DOT = "cl."
    CLEN_ACCENTED = "člen"
    CLEN_ACCENTED_ABBREVIATED = "čl"
    CLEN_ACCENTED_ABBREVIATED_DOT = "čl."


class EntType(str, Enum):
    ID = "ID"
    DOC_ABBR = "DOC_ABBR"
    CLEN = "CLEN"
    CLEN_LEFT = "CLEN_LEFT"
    DOC_TITLE = "DOC_TITLE"
    COURT_AUTHOR = "COURT_AUTHOR"
    STEVNIK = "STEVNIK"
    NUMBER_PLAIN = "NUMBER_PLAIN"  # A number without a dot
    OPOMBE_START = "OPOMBE_START"


class SpanType(str, Enum):
    ZAVRZENJE = "zavrzenje"
    ODLOCITEV = "odlocitev"
    JEDRO_VIR = "jedro_vir"
    NAVEDBA_ZAKONA = "navedba_zakona"
    NAVEDBA_ZAKONA_LEFT = "navedba_zakona_levi"
    NAVEDBA_ZAKONA_RIGHT = "navedba_zakona_desni"
    UTEMELJITEV = "utemeljitev"
    STROSKI = "stroski"
    FEAT_PRED_UTEMELJITVIJO = "se nahaja pred utemeljitvijo"
    FEAT_OPOMBE = "opombe"
    FEAT_V_PRAVNI_PODLAGI = "v pravni podlagi"

    @staticmethod
    def is_navedba_zakona(span):
        return span.label_ in [
            SpanType.NAVEDBA_ZAKONA.value,
            SpanType.NAVEDBA_ZAKONA_LEFT.value,
            SpanType.NAVEDBA_ZAKONA_RIGHT.value,
        ]
