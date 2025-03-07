import re
from collections import defaultdict

from pathlib import Path
from src.nlp.model import EntType
from src.nlp.text_processor import TextProcessor
from src.parse import (
    pdf_to_text,
)
import json

tp = TextProcessor(mappings_path=Path("../../data/mappings/mappings_all.parquet"))


def load_text_from_pdf(file_path: Path):
    return pdf_to_text(file_path=file_path)


def find_laws_in_text(text_to_process: str, gpt_pretty=False):
    text_to_process = text_to_process.replace("\n", " ")
    search_results = tp.nlp(text_to_process)
    entities_types_to_parse = [
        EntType.DOC_TITLE,
        EntType.DOC_ABBR,
        EntType.CLEN,
        EntType.CLEN_LEFT,
    ]

    ents_found = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in search_results.ents if ent.label_ in entities_types_to_parse]
    ents_found = sorted(ents_found, key=lambda x: x[1])

    clusters = find_clusters(ents_found)
    abbr_to_full = find_abbreviations(clusters)
    doc_to_articles = group_articles(clusters, abbr_to_full)
    result = get_title_abbr_article_tuples(abbr_to_full, doc_to_articles)
    if not gpt_pretty:
        result = manually_prettify(result)
    else:
        result = gpt_prettify(result)
    # print(result)
    return result


def find_clusters(ents_found):
    clusters = []
    current_cluster = [ents_found[0]]
    for i in range(1, len(ents_found)):
        if ents_found[i][1] - current_cluster[-1][2] < 3:
            current_cluster.append(ents_found[i])
        elif ents_found[i][1] - current_cluster[-1][2] < 25 and ents_found[i - 1][3] == EntType.DOC_TITLE and ents_found[i][
            3] == EntType.DOC_ABBR:
            current_cluster.append(ents_found[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [ents_found[i]]
    return clusters


def find_abbreviations(clusters):
    abbr_to_full = {}
    for cluster in clusters:
        full_title = None
        abbr = None
        for ent in cluster:
            if ent[3] == EntType.DOC_TITLE:
                full_title = ent[0]
            elif ent[3] == EntType.DOC_ABBR:
                abbr = ent[0]
        if full_title and abbr:
            abbr_to_full[abbr] = full_title
    return abbr_to_full


def get_title_abbr_article_tuples(abbr_to_full, full_to_article):
    full_to_abbr = {v: k for k, v in abbr_to_full.items()}
    results = []
    for full, articles in full_to_article.items():
        abbr = full_to_abbr.get(full, None)
        results.append((full, abbr, articles))
    return results


def group_articles(clusters, abbr_to_full):
    doc_to_article = defaultdict(list)
    for cluster in clusters:
        full_title = None
        abbr = None
        for ent in cluster:
            if ent[3] == EntType.DOC_TITLE:
                full_title = ent[0]
            elif ent[3] == EntType.DOC_ABBR:
                abbr = ent[0]

        for ent in cluster:
            if ent[3] != EntType.CLEN:
                continue
            article = ent[0]
            if full_title:
                doc_to_article[full_title].append(article)
            elif abbr:
                full_title = abbr_to_full.get(abbr, abbr)
                doc_to_article[full_title].append(article)
    return doc_to_article


def manually_prettify(result_list: list[tuple]):
    pretty_strings = []
    for (full, abbr, articles) in result_list:
        pretty_string = f"{full} - "
        if abbr:
            pretty_string += f"{abbr} - "
        pattern = r'(\d+)\.'
        numbers = [int(re.search(pattern, text).group(1)) for text in articles if re.search(pattern, text)]
        numbers = list(set(numbers))
        numbers.sort()
        numbers = [str(x) for x in numbers]
        pretty_string += "člen "+", ".join(numbers)
        pretty_strings.append(pretty_string)
    return pretty_strings


def gpt_prettify(results):
    pass


def add_laws_to_results(results_list: dict):
    for data in results_list["results"]:
        obrazlozitev = data["original"]["obrazlozitev"]
        data["zveza"] = find_laws_in_text(obrazlozitev)
    return results_list


def add_laws_to_results_from_json(json_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    updated_data = add_laws_to_results(data)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=4)


    return add_laws_to_results(data)


if __name__ == "__main__":
    # with open("./../../data/datasets/sample_test_verbatim2.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
    # text_to_process = data[1]["obrazložitev"]

    # find_laws_in_text(text_to_process)
    add_laws_to_results_from_json(Path("./../../results/results_2step_core_verbatim_gemini.json"))