import json
from gpt_utils import call_gpt_json


prompt_combined = """Tvoja naloga je, da iz spodnje sodbe izluščiš **pravni zaključek (jedro)** in nato identificiraš **točne stavke iz sodbe**, ki ta zaključek podpirajo.

Postopek:
1. **Izlušči jedro sodbe**: Povzemi pravni zaključek sodbe v jedrnati obliki, brez opisovanja sodnega postopka, argumentov strank ali napak nižjih sodišč. 
   - Povzetek naj vsebuje **le naslednje ključne elemente**:
     1. **Jedrnato formulirano pravno pravilo** (ključni pravni zaključek, ki ga je sprejelo Vrhovno sodišče).
     2. **Nujna pravna podlaga za ta zaključek** (če je eksplicitno navedena v sodbi – zakon, sodna praksa itd.).
     3. **Brez dodatnih razlag ali postopkovnih ugotovitev** – ne omenjaj argumentov strank, napak nižjih sodišč ali širšega konteksta zadeve.
   - **Ne začni stavka s** *"Vrhovno sodišče je odločilo..."* ali podobnimi frazami.
   - Povzetek mora biti jasen, jedrnat in **neoseben**, oblikovan kot splošno pravno pravilo, ki bi ga lahko neposredno uporabili v podobnih primerih.

2. **Poišči točne citate iz sodbe**, ki pravno utemeljujejo izluščeno jedro.
   - Stavki morajo biti **dobesedni citati iz sodbe**, brez parafraziranja ali dodajanja drugih informacij.
   - Ne vključuj širših razlag, argumentov strank ali postopkovnih ugotovitev – samo tiste dele sodbe, ki pravno utemeljujejo jedro.
   - Če v sodbi ni eksplicitnih stavkov, ki podpirajo jedro, ne dodajaj ničesar – ne poskušaj sklepati ali interpretirati.

### Pričakovan JSON output:
```json
{
   "jedro": "...",
   "podlaga": [
      "Točen citat iz sodbe 1.",
      "Točen citat iz sodbe 2.",
      "Točen citat iz sodbe 3."
   ]
}
"""


def process_files(examples: list[dict], result_filename: str):

    results = []
    for i, data in enumerate(examples):
        print(i)
        izrek = data.get("izrek", "")
        obrazlozitev = data.get("obrazložitev", "")
        jedro = data.get("jedro", "")

        input = "<sodba>" + izrek + obrazlozitev + "</sodba>"
        gpt_result = json.loads(call_gpt_json(prompt_combined, input))
        gpt_jedro = gpt_result['jedro']
        gpt_verbatim = gpt_result['podlaga']

        results_dict = {
            "original": {
                "izrek": izrek,
                "obrazlozitev": obrazlozitev,
                "jedro": jedro
            },
            "gpt_result": {
                "gpt_jedro": gpt_jedro,
                "gpt_verbatim": gpt_verbatim
            },
        }
        results.append(results_dict)
    
    adjusted_results = {"prompt_combined": prompt_combined, "results": results}
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(adjusted_results, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    result_filename = "results_combined_core_verbatim_2.json"
    with open("data/datasets/sample_test_verbatim2.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    process_files(data, result_filename)

