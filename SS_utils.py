import json

from openai import OpenAI

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


def process_files(files):
    # Uporabil sem za 10 datotek, ki so imela verbatim jedro v besedilo
    results = [] 
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            print("Processing file:", file)
            data = json.load(f)
            
            izrek = data.get("content", {}).get("izrek", "")
            obrazlozitev = data.get("content", {}).get("obrazložitev", "")
            jedro = data.get("content", {}).get("jedro", "")
            
            input = "<sodba>" + izrek + obrazlozitev + "</sodba>"
            gpt_result = json.loads(call_gpt_json(prompt, input))
            gpt_jedro = gpt_result['jedro']
            gpt_izrek = gpt_result['izrek']
            
            
            izrek_results = precision_recall_redundancy(gpt_izrek, izrek)
            jedro_results = precision_recall_redundancy(gpt_jedro, jedro)
            
            izrek_verbatim_results = precision_recall_redundancy(gpt_izrek, input)
            jedro_verbatim_results = precision_recall_redundancy(gpt_jedro, input)
            
            
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
                    "izrek_results": izrek_results,
                    "jedro_results": jedro_results
                },
                "evaluation_verbatim":{
                    "izrek_verbatim": izrek_verbatim_results,
                    "jedro_verbatim": jedro_verbatim_results,
                }
            }        
            results.append(results_dict)

        
    with open('results.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
