import json
import re
import rapidfuzz as rf
from openai import OpenAI
from bs4 import BeautifulSoup
from html_output import apply_styles, save_html_to_file

api_key = ""
client = OpenAI(api_key = api_key)

prompt = """
Tvoja naloga je iz priložene sodbe (označene z <sodba></sodba>) izluščiti jedro ter izrek.

Pojmi:
- Izrek: To je končna odločitev sodišča, ki določa pravni položaj strank (npr. „obtožba se zavrne“ ali „tožena stranka naj plača določen znesek“). V praksi je izrek formalno najpomembnejši, a ne opisuje nujno temeljnega pravnega argumenta, po katerem je sodišče odločilo.
- Jedro: Kratek, samostojen povzetek odločilnega pravnega stališča oziroma nosilnega razloga (ratio decidendi). Jedro navadno osvetli, kako se v konkretnem primeru uporabi zakonska ali sodna norma (npr. člen OZ, ZKP itd.) in v čem je ključen pomen te razlage. Lahko je krajši ali daljši odstavek.

Tako jedro in izrek najdi iz direktno iz besedila. Ne parafriziraj, uporabi stavke iz sodbe, stavki so lahko iz različnih odstavkov v sodbi, a morejo biti identični!

Pričakovan output je validen json:
{"izrek":..., "jedro":....}
"""


def call_gpt(prompt: str, input_text: str, temperature=0.1) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text},
        ],
    )
    return response.choices[0].message.content

def call_gpt_json(prompt: str, input_text: str, temperature=0.1) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text},
        ],
        response_format={ "type": "json_object" }
    )
    return response.choices[0].message.content

def precision_recall_redundancy(extracted_text: str, ground_truth_text: str):
    "Comparisons of substrings/words"
    extracted_tokens = set(extracted_text.split())
    ground_truth_tokens = set(ground_truth_text.split())

    intersection = extracted_tokens & ground_truth_tokens

    precision = len(intersection) / len(extracted_tokens) if extracted_tokens else 0  # How much of the extracted text is actually correct
    recall = len(intersection) / len(ground_truth_tokens) if ground_truth_tokens else 0 # How much of the ground truth was successfully extraced
    length_redundancy_ratio = len(extracted_tokens) / len(ground_truth_tokens) if ground_truth_tokens else 0 # How much extra text in extracted text

    return {
        "precision": precision,
        "recall": recall,
        "redundancy_ratio": length_redundancy_ratio
    }


def text_similarity(text, corpus):
    if len(text) >= len(corpus):
        corpus += " " * (len(text) - len(corpus) + 1)
    chars_found = 0
    total_length = 0
    match_intervals = []
    split = re.split(r'[,.]', text)
    split = [x.strip() for x in split]
    for piece in split:
        total_length += len(piece)
        match = rf.fuzz.partial_ratio_alignment(piece, corpus)
        if match.score > 80:
            chars_found += len(piece)
            match_intervals.append((match.dest_start, match.dest_end))
    # print(match_intervals)
    values = []
    for (a, b) in match_intervals:
        values += list(range(a, b))
    text_covered = len(set(values))

    split_corpus = re.split(r'[,.]', corpus)
    split_corpus = [x.strip() for x in split_corpus]
    corpus_length = sum([len(c) for c in split_corpus])

    if corpus_length == 0:
        breakpoint()
    recall = text_covered / corpus_length
    precision = chars_found / total_length
    return precision, recall, match_intervals


def process_files(examples: list[dict], result_filename: str):

    results = []
    for i, data in list(enumerate(examples)):
        print(i)
        izrek = data.get("izrek", "")
        obrazlozitev = data.get("obrazložitev", "")
        jedro = data.get("jedro", "")

        input = "<sodba>" + izrek + obrazlozitev + "</sodba>"
        gpt_result = json.loads(call_gpt_json(prompt, input))
        gpt_jedro = gpt_result['jedro']
        gpt_izrek = gpt_result['izrek']

        izrek_gt_results = text_similarity(izrek, input)
        jedro_gt_results = text_similarity(jedro, input)

        izrek_results = text_similarity(gpt_izrek, izrek)
        jedro_results = text_similarity(gpt_jedro, jedro)

        izrek_verbatim_results = text_similarity(gpt_izrek, input)
        jedro_verbatim_results = text_similarity(gpt_jedro, input)

        html_output = apply_styles(input, jedro_verbatim_results[2], jedro_gt_results[2])
        save_html_to_file(html_output,
                          [jedro, gpt_jedro, "Precision: {:.2f}, Recall: {:.2f}".format(jedro_results[0], jedro_results[1])],
                          f"./htmls/example_{i}.html")

        results_dict = {
            "original": {
                "izrek": izrek,
                "obrazlozitev": obrazlozitev,
                "jedro": jedro
            },
            "gpt_result": {
                "gpt_izrek": gpt_izrek,
                "gpt_jedro": gpt_jedro
            },
            "evaluation": {
                "izrek_results": izrek_results[:2],
                "jedro_results": jedro_results[:2],
            },
            "evaluation_verbatim":{
                "izrek_verbatim": izrek_verbatim_results[:2],
                "jedro_verbatim": jedro_verbatim_results[:2],
            }
        }
        results.append(results_dict)

    print(results)
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    result_filename = "results.json"
    with open("./data/datasets/sample_test_verbatim.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    process_files(data, result_filename)
