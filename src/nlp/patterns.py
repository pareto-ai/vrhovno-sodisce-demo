from src.nlp.model import ClenCombinations, EntType, SpanType


ENTITY_PATTERNS = [
    {
        "label": EntType.ID.value,
        "pattern": [
            {"TEXT": {"REGEX": r"^\d{1,10}$"}},
            {"ORTH": "-"},
            {"TEXT": {"REGEX": r"^\d{1,10}\/\d{4}$"}},
        ],
    },
    {
        "label": EntType.ID.value,
        "pattern": [
            {"TEXT": {"REGEX": r"^\d{1,10}$"}},
            {"ORTH": "-"},
            {"TEXT": {"REGEX": r"^\d{1,10}$"}},
            {"ORTH": "/"},
            {"TEXT": {"REGEX": r"^\d{1,4}$"}},
        ],
    },
    {
        "label": EntType.ID.value,
        "pattern": [{"TEXT": {"REGEX": r"\d{1,10}\/\d{4}"}}],
    },
    {
        "label": EntType.STEVNIK.value,
        "pattern": [
            {"TEXT": {"REGEX": r"^[0-9]{1,4}\.$"}},
        ],
    },
    {
        "label": EntType.NUMBER_PLAIN.value,
        "pattern": [
            {"TEXT": {"REGEX": r"^\d{1,4}$"}},
        ],
    },
    {
        "label": EntType.CLEN.value,
        "pattern": [
            {"TEXT": {"REGEX": r"\d{1,4}\.\w?"}},
            {"LEMMA": {"IN": [x.value for x in ClenCombinations]}},
        ],
    },
    {
        "label": EntType.CLEN.value,
        "pattern": [
            {"TEXT": {"REGEX": r"\d{1,4}\."}},
            {"TEXT": {"REGEX": r"\w"}},
            {"LEMMA": {"IN": [x.value for x in ClenCombinations]}},
        ],
    },
    {
        "label": EntType.CLEN.value,
        "pattern": [
            {"TEXT": {"REGEX": r"\d{1,4}$"}},
            {"ORTH": ".", "OP": "?"},
            {"TEXT": {"REGEX": r"\w"}, "OP": "?"},
            {"LEMMA": {"IN": [x.value for x in ClenCombinations]}},
        ],
    },
    {
        "label": EntType.CLEN_LEFT.value,
        "pattern": [
            {"LEMMA": {"IN": [x.value for x in ClenCombinations]}},
            {"TEXT": {"REGEX": r"\d{1,4}\.$"}},
            {"TEXT": {"REGEX": r"^\w$"}, "OP": "?"},
        ],
    },
    {
        "label": EntType.CLEN_LEFT.value,
        "pattern": [
            {"LEMMA": {"IN": [x.value for x in ClenCombinations]}},
            {"TEXT": {"REGEX": r"\d{1,4}$"}},
            {"ORTH": ".", "OP": "?"},
            {"TEXT": {"REGEX": r"^\w$"}, "OP": "?"},
        ],
    },
    {
        "label": EntType.OPOMBE_START.value,
        "pattern": [
            {"TEXT": {"REGEX": r"^[-]$"}, "OP": "{3,}"},
            {"ORTH": "<"},
            {"ORTH": "br"},
            {"ORTH": "/"},
            {"ORTH": ">"},
        ],
    },
]

SPAN_PATTERNS = [
    {
        "label": SpanType.NAVEDBA_ZAKONA.value,
        "pattern": [
            {"ENT_TYPE": {"IN": [EntType.CLEN.value, EntType.CLEN_LEFT.value]}},
            {"ENT_TYPE": {"IN": [EntType.DOC_TITLE.value, EntType.DOC_ABBR.value]}},
        ],
    },
    {
        "label": SpanType.NAVEDBA_ZAKONA.value,
        "pattern": [
            {"ENT_TYPE": EntType.NUMBER_PLAIN.value},
            {"ENT_TYPE": {"IN": [EntType.DOC_TITLE.value, EntType.DOC_ABBR.value]}},
        ],
    },
    {
        # Ex: Pritožba ni utemeljena.
        # Ex: Pritožba je neutemeljena.
        # Ex: Pritožba je v večjem delu utemeljena.
        # Ex: Ugovor in pritožba nista utemeljena.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["revizija", "pritožba", "tožba", "predlog", "ugovor"]},
                "IS_TITLE": True,
            },
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "biti"},
            {"OP": "?"},
            {"OP": "?"},
            {"OP": "?"},
            {
                "LEMMA": {
                    "IN": [
                        "utemeljen",
                        "neutemeljen",
                    ]
                }
            },
        ],
    },
    {
        # Ex: Predlog ni dovoljen.
        # Ex: Predlog ni popoln.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["predlog"]},
                "IS_TITLE": True,
            },
            {"TEXT": {"REGEX": r"[^\.,]"}, "OP": "*"},
            {"LEMMA": "biti"},
            {"OP": "?"},
            {"OP": "?"},
            {"LEMMA": {"IN": ["dovoljen", "popoln", "prepozen", "nedovoljen"]}},
        ],
    },
    {
        # Ex: Predlog za obnovo postopka, ki ga je 27.12.2001 vložil pooblaščeni F. M., univ. dipl. prav., ni dovoljen.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["predlog"]},
                "IS_TITLE": True,
            },
            {"LEMMA": "za"},
            {"LEMMA": "obnova"},
            {"LEMMA": "postopek"},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "biti"},
            {"LEMMA": {"IN": ["dovoljen", "prepozen"]}},
        ],
    },
    {
        # Ex: Predlog je v delu, razvidnem iz izreka sklepa, utemeljen.
        # This is separate as above, since * matching can blow up if not contained.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["predlog"]},
                "IS_TITLE": True,
            },
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "razviden"},
            {"LEMMA": "iz"},
            {"LEMMA": "izrek"},
            {"LEMMA": "sklep"},
            {"OP": "?"},
            {"OP": "?"},
            {"OP": "?"},
            {
                "LEMMA": {
                    "IN": [
                        "utemeljen",
                        "neutemeljen",
                    ]
                }
            },
        ],
    },
    {
        # Ex: Tožba ni dopustna.
        # Ex: Tožba ni dovoljena.
        # Ex: Tožbo je potrebno zavreči.
        # Ex: Tožba v delu, ki se nanaša na zakonitost odločbe v delu,
        #     v katerem je odmerjeno nadomestilo za degradacijo in
        #     uzurpacijo prostora A.A., ni dovoljena.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["revizija", "pritožba", "tožba"]},
                "IS_TITLE": True,
            },
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "biti"},
            {"OP": "?"},
            {"OP": "?"},
            {"LEMMA": {"IN": ["dopusten", "zavreči", "dovoljen"]}},
        ],
    },
    {
        # Ex: Tožba se zavrže.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["revizija", "pritožba", "tožba"]},
                "IS_TITLE": True,
            },
            {"LEMMA": "se"},
            {"OP": "?"},
            {"OP": "?"},
            {
                "LEMMA": {
                    "IN": [
                        "zavrniti",
                        "zavreči",
                    ]
                }
            },
        ],
    },
    {
        # Ex:  Pregled zadeve na pritožbeni stopnji je pokazal,
        #      da je pritožba zagovornice obdolžene delno utemeljena.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["pritožben"]},
            },
            {
                "LEMMA": {"IN": ["stopnja"]},
            },
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "biti"},
            {
                "LEMMA": {"IN": ["pritožba"]},
            },
            {"TEXT": {"REGEX": r"[^\.,]"}, "OP": "*"},
            {
                "LEMMA": {
                    "IN": [
                        "utemeljen",
                        "neutemeljen",
                    ]
                }
            },
        ],
    },
    {
        # Ex: Pregled zadeve na pritožbeni stopnji je pokazal, da pritožba ni utemeljena.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["pritožben"]},
            },
            {
                "LEMMA": {"IN": ["stopnja"]},
            },
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {
                "LEMMA": {"IN": ["pritožba"]},
            },
            {"LEMMA": "biti"},
            {
                "LEMMA": {
                    "IN": [
                        "utemeljen",
                        "neutemeljen",
                    ]
                }
            },
        ],
    },
    {
        # Ex:  Utemeljena je le pritožba okrožne državne tožilke
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {
                    "IN": [
                        "utemeljen",
                        "neutemeljen",
                    ]
                },
                "IS_TITLE": True,
            },
            {"LEMMA": "biti"},
            {"OP": "?"},
            {
                "LEMMA": {"IN": ["pritožba"]},
            },
        ],
    },
    {
        # Ex: Razlogi za zavrnitev revizije
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "razlog"},
            {"LEMMA": "za"},
            {"LEMMA": "zavrnitev"},
            {"LEMMA": "revizija"},
        ],
    },
    {
        # Ex: Presoja utemeljenosti revizije: revizija ni utemeljena.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "presoja"},
            {"LEMMA": "utemeljenost"},
            {"LEMMA": "revizija"},
            {"ORTH": ":"},
            {"LEMMA": "revizija"},
            {"LEMMA": "biti"},
            {
                "LEMMA": {
                    "IN": [
                        "utemeljen",
                        "neutemeljen",
                    ]
                }
            },
        ],
    },
    {
        # Ex: Zoper sodbo sodišča druge stopnje je tožeča stranka vložila revizijo zaradi
        # zmotne uporabe materialnega prava, nato pa je z vlogo z dne
        # 30. 6. 2017 revizijo umaknila ...
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "tožeč"},
            {"LEMMA": "stranka"},
            {"LEMMA": "vložiti"},
            {"LEMMA": "revizija"},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "revizija"},
            {"LEMMA": "umakniti"},
        ],
    },
    {
        # Ex: Sodišče je predlogu za izdajo začasne odredbe ugodilo iz naslednjih razlogov:
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "sodišče"},
            {"LEMMA": "biti"},
            {"LEMMA": "predlog"},
            {"LEMMA": "za"},
            {"LEMMA": "izdaja"},
            {"LEMMA": "začasen"},
            {"LEMMA": "odredba"},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "ugoditi"},
            {"LEMMA": "iz"},
            {"LEMMA": "naslednji"},
            {"LEMMA": "razlog"},
        ],
    },
    {
        # Ex: Izpodbijano sodbo je bilo potrebno razveljaviti po uradni dolžnosti
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "izpodbijan"},
            {"LEMMA": "sodba"},
            {"LEMMA": "biti"},
            {"TEXT": {"REGEX": r"[^\.,]"}, "OP": "*"},
            {"LEMMA": "razveljaviti"},
        ],
    },
    {
        # Ex: Ugovor je prepozen.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["ugovor", "revizija"]},
                "IS_TITLE": True,
            },
            {"LEMMA": {"IN": ["biti", "se"]}},
            {
                "LEMMA": {
                    "IN": [
                        "prepozen",
                        "prepoznati",  # The lemmatizer is sometimes wrong
                    ]
                }
            },
        ],
    },
    {
        # Ex: Zahteva za varstvo zakonitosti ni utemeljena.
        # Ex: Zahteve zagovornikov obsojenih R.V. in G.V. za varstvo zakonitosti niso utemeljene
        # Ex: Zahteva za varstvo zakonitosti ni dovoljena.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["zahteva", "zahtevati"]},
                "IS_TITLE": True,
            },
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "za"},
            {"LEMMA": "varstvo"},
            {"LEMMA": "zakonitost"},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "biti"},
            {"OP": "?"},
            {"OP": "?"},
            {"LEMMA": {"IN": ["utemeljen", "neutemeljen", "dovoljen"]}},
        ],
    },
    {
        # Ex: Zahteva zoper pravnomočni sklep o zavrnitvi zahteve
        #     za obnovo kazenskega postopka ni utemeljena.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["zahteva"]},
                "IS_TITLE": True,
            },
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "biti"},
            {"LEMMA": {"IN": ["utemeljen", "neutemeljen"]}},
        ],
    },
    {
        # Ex: Zahteva za izredno omilitev kazni ni utemeljena.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["zahteva"]},
                "IS_TITLE": True,
            },
            {"LEMMA": "za"},
            {"LEMMA": "izreden"},
            {"LEMMA": "omilitev"},
            {"LEMMA": "kazen"},
            {"LEMMA": "biti"},
            {"OP": "?"},
            {"OP": "?"},
            {"LEMMA": {"IN": ["utemeljen", "neutemeljen"]}},
        ],
    },
    {
        # Ex: je pristojno Okrajno sodišče na Vrhniki.
        # Ex: je pristojno Okrajno sodišče v Celju.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "biti"},
            {"OP": "{,5}"},
            {"LEMMA": "pristojen"},
            {"OP": "?"},
            {"LEMMA": "sodišče"},
            {"LEMMA": {"IN": ["v", "na"]}},
            {"TEXT": {"REGEX": r"[^\.,]"}, "OP": "*"},
            {"ORTH": "."},
        ],
    },
    {
        # Ex: Upravno sodišče RS ni stvarno pristojno za odločanje v tej zadevi.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "sodišče"},
            {},
            {"LEMMA": "Slovenija", "OP": "?"},
            {"LEMMA": {"IN": ["biti", "se"]}},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": {"IN": ["pristojen", "nepristojen"]}},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "{,5}"},
            {"ORTH": "."},
        ],
    },
    {
        # Ex: Tožbi je sodišče ugodilo zaradi naslednjih razlogov:
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {
                "LEMMA": {"IN": ["revizija", "pritožba", "tožba", "predlog"]},
                "IS_TITLE": True,
            },
            {"LEMMA": "biti"},
            {"LEMMA": "sodišče"},
            {"LEMMA": {"IN": ["zavrniti", "ugoditi"]}},
        ],
    },
    {
        # Ex: Sodišče je tožbi ugodilo iz naslednjih razlogov
        # Ex: Sodišče je moralo tožbo zavreči iz naslednjih razlogov
        # Ex: Upravno sodišče Republike Slovenije je tožbo zavrglo iz naslednjih razlogov:
        # Ex: sodišče ugotovilo, da je tožbo treba zavreči kot prepozno
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "sodišče"},
            {"LEMMA": {"NOT_IN": ["stopnja"]}, "OP": "?"},
            {"LEMMA": {"NOT_IN": ["stopnja"]}, "OP": "?"},
            {"LEMMA": {"NOT_IN": ["stopnja"]}, "OP": "?"},
            {"LEMMA": "biti"},
            {"OP": "?"},
            {"LEMMA": {"IN": ["revizija", "pritožba", "tožba"]}},
            {"OP": "?"},
            {"LEMMA": {"IN": ["zavrniti", "ugoditi", "zavreči"]}},
        ],
    },
    {
        # Ex: Sodišče druge stopnje je v delu, relevantnem za odločitev
        #     o predlogu za dopustitev revizije, pritožbo tožene stranke zavrnilo
        # As this is a very specific example, we are being conservative to avoid FPs.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "sodišče"},
            {"LEMMA": "drug"},
            {"LEMMA": "stopnja"},
            {"LEMMA": "biti"},
            {"LEMMA": "v"},
            {"LEMMA": "del"},
            {"ORTH": ","},
            {"LEMMA": "relevanten"},
            {"LEMMA": "za"},
            {"LEMMA": "odločitev"},
            {"LEMMA": "o"},
            {"LEMMA": "predlog"},
            {"LEMMA": "za"},
            {"LEMMA": "dopustitev"},
            {"LEMMA": "revizija"},
            {"ORTH": ","},
            {"LEMMA": "pritožba"},
            {"LEMMA": "tožen"},
            {"LEMMA": "stranka"},
            {"LEMMA": "zavrniti"},
        ],
    },
    {
        # Ex: Pritožbeni postopek se prekine.
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"LEMMA": "pritožben"},
            {"LEMMA": "postopek"},
            {"LEMMA": "se"},
            {"LEMMA": "prekiniti"},
        ],
    },
    {
        # Ex: Sekcije B, B-1
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"_": {"html_break": True}},
            {"TEXT": {"REGEX": r"^B\.?$"}},
            {"ORTH": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"^[1I]\.?$"}, "OP": "?"},
            {"ORTH": ".", "OP": "?"},
            {"_": {"html_break": True}},
        ],
    },
    {
        # Ex: Sekcije B, B-1 with <p> tags -> they are not considered html_break
        # in old texts
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"ORTH": "<"},
            {"ORTH": "p"},
            {"ORTH": ">"},
            {"TEXT": {"REGEX": r"^B\.?$"}},
            {"ORTH": "-", "OP": "?"},
            {"TEXT": {"REGEX": r"^[1I]\.?$"}, "OP": "?"},
            {"ORTH": ".", "OP": "?"},
            {"ORTH": {"IN": ["<", "</p>"]}},
        ],
    },
    {
        # Ex: "K 1. točki izreka", "K 2. točki izreka"
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"_": {"html_break": True}},
            {"LEMMA": "k"},
            {"ENT_TYPE": EntType.STEVNIK.value},
            {"LEMMA": "točka"},
            {"LEMMA": "izrek"},
        ],
    },
    {
        # Ex: <p>"K 1. točki izreka", "K 2. točki izreka"
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"ORTH": "<"},
            {"ORTH": "p"},
            {"ORTH": ">"},
            {"LEMMA": "k"},
            {"ENT_TYPE": EntType.STEVNIK.value},
            {"LEMMA": "točka"},
            {"LEMMA": "izrek"},
        ],
    },
    {
        # Ex: "K I. točki izreka"
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"_": {"html_break": True}},
            {"LEMMA": "k"},
            {"TEXT": {"REGEX": r"^(I|II|III|IV|V).$"}, "OP": "*"},
            {"LEMMA": "točka"},
            {"LEMMA": "izrek"},
        ],
    },
    {
        # Ex: "K I. točki izreka"
        "label": SpanType.UTEMELJITEV.value,
        "pattern": [
            {"ORTH": "<"},
            {"ORTH": "p"},
            {"ORTH": ">"},
            {"LEMMA": "k"},
            {"TEXT": {"REGEX": r"^(I|II|III|IV|V).$"}, "OP": "*"},
            {"LEMMA": "točka"},
            {"LEMMA": "izrek"},
        ],
    },
    {
        "label": SpanType.ZAVRZENJE.value,
        "pattern": [
            {"LEMMA": {"IN": ["revizija", "predlog", "pritožba", "tožba", "pobuda"]}},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "se"},
            {"OP": "?"},
            {"OP": "?"},
            {"LEMMA": {"IN": ["zavreči"]}},
        ],
    },
    {
        "label": SpanType.ZAVRZENJE.value,
        "pattern": [
            {"LEMMA": "se"},
            {"LEMMA": {"IN": ["revizija", "predlog", "pritožba", "tožba"]}},
            {"LEMMA": {"IN": ["zavreči"]}},
        ],
    },
    {
        "label": SpanType.ZAVRZENJE.value,
        "pattern": [
            {"LEMMA": {"IN": ["predlog"]}},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": {"IN": ["umaknjen"]}},
        ],
    },
    {
        "label": SpanType.ZAVRZENJE.value,
        "pattern": [
            {"LEMMA": "revizija"},
            {"LEMMA": "se"},
            {"LEMMA": "dopustiti"},
            {"LEMMA": "glede"},
            {"LEMMA": "vprašanje"},
        ],
    },
    {
        "label": SpanType.ZAVRZENJE.value,
        "pattern": [
            {"LEMMA": {"IN": ["zahteva", "zahtevati"]}},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "za"},
            {"LEMMA": "varstvo"},
            {"LEMMA": "zakonitost"},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "se"},
            {"LEMMA": {"IN": ["zavreči"]}},
        ],
    },
    {
        "label": SpanType.ODLOCITEV.value,
        "pattern": [
            {"LEMMA": {"IN": ["revizija", "pritožba", "tožba"]}},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "se"},
            {"OP": "?"},
            {"OP": "?"},
            {"LEMMA": {"IN": ["zavrniti", "ugoditi"]}},
        ],
    },
    {
        "label": SpanType.ODLOCITEV.value,
        "pattern": [
            {"LEMMA": {"IN": ["zahteva", "zahtevati"]}},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "za"},
            {"LEMMA": "varstvo"},
            {"LEMMA": "zakonitost"},
            {"TEXT": {"REGEX": r"[^\.]"}, "OP": "*"},
            {"LEMMA": "se"},
            {"LEMMA": {"IN": ["zavrniti", "ugoditi"]}},
        ],
    },
    {
        "label": SpanType.ODLOCITEV.value,
        "pattern": [
            {"LEMMA": "se"},
            {"LEMMA": {"IN": ["revizija", "pritožba", "tožba"]}},
            {"LEMMA": {"IN": ["zavrniti", "ugoditi"]}},
        ],
    },
    {
        "label": SpanType.STROSKI.value,
        "pattern": [
            {"LEMMA": "izrek"},
            {"LEMMA": {"IN": ["o"]}},
            {"LEMMA": {"IN": ["strošek"]}},
        ],
    },
]
