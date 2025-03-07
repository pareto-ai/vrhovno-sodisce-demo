import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import anthropic

client_claude = anthropic.Anthropic(
    api_key="",
)

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)


def call_claude_json(prompt: str, input_text: str, temperature=0.1) -> str:
    response = client_claude.messages.create(
        model="claude-3-5-sonnet-latest",  # Use the latest Claude model available
        temperature=temperature,
        system=prompt,
        max_tokens=2024,
        messages=[{"role": "user", "content": input_text}],
    )
    return response.content[0].text

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

def call_google(prompt: str, input_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text},
        ],
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="Naredi jedro"
    )
    return response.choices[0].message.content

prompt_core = """Pripravi jedro sodbe Vrhovnega sodišča, ki obravnava revizijo v civilni zadevi. V spodnjem besedilu je zajeta daljša obrazložitev sodbe, ki jo želimo strnjeno povzeti. 

Tvoja naloga je, da izluščiš **le pravni zaključek sodbe**, brez opisovanja sodnega postopka ali napak nižjih sodišč. 

Povzetek naj vsebuje **le naslednje ključne elemente**:
1. **Jedrnato formulirano pravno pravilo** (ključni pravni zaključek, ki ga je sprejelo Vrhovno sodišče). 
2. **Nujna pravna podlaga za ta zaključek** (če je eksplicitno navedena v sodbi – zakon, sodna praksa itd.).
3. **Brez dodatnih razlag ali postopkovnih ugotovitev** – ne omenjaj argumentov strank, napak nižjih sodišč ali širšega konteksta zadeve. Osredotoči se izključno na končno pravno rešitev.

⚠ **Pomembno**:
- Ne začni stavka s *"Vrhovno sodišče je odločilo..."* ali podobnimi frazami.
- Povzetek mora biti jasen, jedrnat in **neoseben**, oblikovan kot splošno pravno pravilo,  ki bi ga lahko neposredno uporabili v podobnih primerih. 

Pričakovan output je validen JSON:
```json
{"jedro": "..."}

Sodba bo podana v <sodba></sodba>
"""


prompt_find_verbatim = """
Podano je **že izluščeno pravno jedro** v <jedro></jedro> in **celotno besedilo sodbe** v <sodba></sodba>. Tvoja naloga je, da v sodbi poiščeš **točne stavke**, ki so podlaga za to jedro.

### Navodila:
1. Preglej sodbo in **identificiraj stavke, ki neposredno podpirajo pravno jedro**.
2. Stavki morajo biti **dobesedni citati iz sodbe**, brez parafraziranja.
3. Ne vključuj širših razlag, argumentov strank ali postopkovnih ugotovitev – samo tiste dele sodbe, ki pravno utemeljujejo jedro.
4. Vrni rezultat v naslednjem formatu:
   ```json
   {
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
        gpt_result = json.loads(call_gpt_json(prompt_core, input))
        gpt_jedro = gpt_result['jedro']

        input = "<jedro>" + gpt_jedro + "</jedro>" + input
        gpt_verbatim_results = json.loads(call_gpt_json(prompt_find_verbatim, input))
        gpt_verbatim = gpt_verbatim_results['podlaga']

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
    
    adjusted_results = {'prompt_core': prompt_core, "prompt_find_verbatim": prompt_find_verbatim, "results": results}
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(adjusted_results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    result_filename = "results_2step_core_verbatim.json"
    with open("./data/datasets/sample_test_verbatim.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    process_files(data[:10], result_filename)




