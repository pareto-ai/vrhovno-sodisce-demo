import json

from gpt_utils import call_gpt_json

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


prompt_core_improved = """Pripravi jedro sodbe Vrhovnega sodišča, ki obravnava revizijo v civilni zadevi. V spodnjem besedilu je zajeta daljša obrazložitev sodbe, ki jo želimo strnjeno povzeti. 

Tvoja naloga je, da izluščiš **le pravni zaključek sodbe**, brez opisovanja sodnega postopka ali napak nižjih sodišč. 

Povzetek naj vsebuje **le naslednje ključne elemente**:
1. **Jedrnato formulirano pravno pravilo** (ključni pravni zaključek, ki ga je sprejelo Vrhovno sodišče). 
2. **Nujna pravna podlaga za ta zaključek** (če je eksplicitno navedena v sodbi – zakon, sodna praksa itd.) mora biti vključena neposredno v stavek, bodisi kot del besedila bodisi v oklepaju. Celotno ime zakona omeni le v primeru obskurnih zakonikov/zakonov iz EU, v vseh ostalih primerih uporabi kratice zakonov - nikoli pa obojega!

    **PRAVILNO**:
   - *V primeru prestavitve služnostne poti mora lastnik služeče nepremičnine kriti stroške vzpostavitve nove poti, vključno s sistemom odvodnjavanja in tlakovanjem v skladu s tretjim odstavkom 219. člena SPZ*  
   
    **NEPRAVILNO** (pravna podlaga podana kot ločen stavek):  
   - *V primeru prestavitve služnostne poti mora lastnik služeče nepremičnine kriti stroške vzpostavitve nove poti, vključno s sistemom odvodnjavanja in tlakovanjem. Pravna podlaga za ta zaključek je smiselna razlaga tretjega odstavka 219. člena Stvarnopravnega zakonika (SPZ).*  
   
3. **Brez dodatnih razlag ali postopkovnih ugotovitev** – ne omenjaj argumentov strank, napak nižjih sodišč ali širšega konteksta zadeve. Osredotoči se izključno na končno pravno rešitev.

⚠ **Pomembno**:
- Ne začni stavka s *"Vrhovno sodišče je odločilo..."* ali podobnimi frazami.
- Povzetek mora biti jasen, jedrnat in **neoseben**, oblikovan kot splošno pravno pravilo, ki bi ga lahko neposredno uporabili v podobnih primerih. 

### Pričakovan output:
Vrni validen JSON v naslednji obliki:
```json
{"jedro": "..."}
"""

prompt_core_sklep = """Pripravi jedro sklepa Vrhovnega sodišča v civilni zadevi. V spodnjem besedilu je obrazložitev procesne odločitve (sklepa), ki jo želimo strnjeno povzeti.

Tvoja naloga je, da izluščiš bistvo sklepa, ki je praviloma procesne narave (npr. zavrženje, zavrnitev predloga, razveljavitev odločbe nižjega sodišča).

Povzetek naj vsebuje **le naslednje ključne elemente**:
1. **Procesno odločitev Vrhovnega sodišča** (zavrženje, zavrnitev, razveljavitev ipd.).
2. **Pravno podlago za to odločitev** (konkretni člen zakona, na podlagi katerega je Vrhovno sodišče sprejelo svojo odločitev) - navedena naj bo v oklepaju ali kot del stavka.

**NUJNO UPOŠTEVAJ**:
- Sklepi se ukvarjajo s procesnimi predpostavkami in ne z vsebino spora, zato NE išči vsebinskih meritorno-pravnih zaključkov.
- Glavni poudarek je na odločitvi sodišča o procesnih vprašanjih.
- Uporabljaj pasiv v sedanjiku, ne aktiva!
- Uporabljaj kratice zakonov (ZPP, OZ, SPZ, itd.) namesto polnih imen, razen pri manj znanih zakonih.


### Pričakovan output:
Vrni validen JSON v naslednji obliki:
```json
{"jedro": "..."}
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


prompt_find_verbatim_improved = """
Podano je **že izluščeno pravno jedro** v <jedro></jedro> in **celotno besedilo sodbe** v <sodba></sodba>. Tvoja naloga je, da v sodbi poiščeš **točne stavke**, ki so neposredna podlaga za to jedro.

### Navodila:
1. Preglej sodbo in **identificiraj stavke, ki neposredno podpirajo pravno jedro**.
   - Stavek neposredno podpira jedro, če vsebuje konkreten pravni zaključek ali pravilo, na katerem jedro temelji.

2. Stavki morajo biti **dobesedni citati iz sodbe**, brez sprememb ali parafraziranja.

3. **Ne vključuj**:
   - Širših razlag, ki niso nujne za razumevanje jedra
   - Argumentov strank v postopku
   - Postopkovnih ugotovitev
   - Kontekstualnih informacij, ki niso del pravne utemeljitve
   
4. **Išči minimalno število stavkov**:
- Vključi samo tiste stavke, ki so nujno potrebni za podporo pravnemu jedru.
- Ne podvajaj informacij – če več stavkov izraža isto pravno načelo, izberi samo najjasnejšega.
- Cilj je najti najboljšo, ne najobsežnejšo podlago.

5. Vrni rezultat v naslednjem formatu:
```json
{
  "podlaga": [
    "Točen citat iz sodbe 1.",
    "Točen citat iz sodbe 2."
  ]
}
"""


prompt_find_verbatim_sklep = """
Podano je **že izluščeno pravno jedro** v <jedro></jedro> in **celotno besedilo sodbe** v <sodba></sodba>. Tvoja naloga je, da v sodbi poiščeš **točne stavke**, ki so neposredna podlaga za to jedro.

### Navodila:
1. Preglej sodbo in **identificiraj stavke, ki neposredno podpirajo pravno jedro**.
   - Stavek neposredno podpira jedro, če vsebuje konkreten pravni zaključek ali pravilo, na katerem jedro temelji.

2. Stavki morajo biti **dobesedni citati iz sodbe**, brez sprememb ali parafraziranja.

3. **Ne vključuj**:
   - Širših razlag, ki niso nujne za razumevanje jedra
   - Kontekstualnih informacij, ki niso del pravne utemeljitve
   
4. **Išči minimalno število stavkov**:
- Vključi samo tiste stavke, ki so nujno potrebni za podporo pravnemu jedru.
- Ne podvajaj informacij – če več stavkov izraža isto pravno načelo, izberi samo najjasnejšega.
- Cilj je najti najboljšo, ne najobsežnejšo podlago.

5. Vrni rezultat v naslednjem formatu:
```json
{
  "podlaga": [
    "Točen citat iz sodbe 1.",
    "Točen citat iz sodbe 2."
  ]
}
"""

def process_sodba_files(examples: list[dict], result_filename: str):

    results = []
    for i, data in enumerate(examples):
        print(i)
        izrek = data.get("izrek", "")
        obrazlozitev = data.get("obrazložitev", "")
        jedro = data.get("jedro", "")

        input = "<sodba>" + izrek + obrazlozitev + "</sodba>"
        
        gpt_result = json.loads(call_gpt_json(prompt_core, input))
        gpt_jedro = gpt_result['jedro']
        
        gpt_sklep_results = json.loads(call_gpt_json(prompt_core_sklep, input))
        gpt_sklep = gpt_sklep_results['jedro']
        
        input = "<jedro>" + gpt_jedro + "</jedro>" + input
        gpt_verbatim_results = json.loads(call_gpt_json(prompt_find_verbatim, input))
        gpt_verbatim = gpt_verbatim_results['podlaga']

        gpt_verbatim_improved_results = json.loads(call_gpt_json(prompt_find_verbatim_improved, input))
        gpt_verbatim_improved = gpt_verbatim_improved_results['podlaga']


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
            "gpt_result_improved": {
                "gpt_jedro": gpt_sklep,
                "gpt_verbatim": gpt_verbatim_improved
            },
        }
        results.append(results_dict)
    
    adjusted_results = {'prompt_core': prompt_core, "prompt_find_verbatim": prompt_find_verbatim, 'prompt_core_improved': prompt_core_improved, "prompt_find_verbatim_improved": prompt_find_verbatim_improved, "results": results}
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(adjusted_results, f, ensure_ascii=False, indent=4)




def process_sklep_files(examples: list[dict], result_filename: str):

    results = []
    for i, data in enumerate(examples):
        print(i)
        izrek = data.get("izrek", "")
        obrazlozitev = data.get("obrazložitev", "")
        jedro = data.get("jedro", "")

        input = "<sodba>" + izrek + obrazlozitev + "</sodba>"
        
        gpt_result = json.loads(call_gpt_json(prompt_core, input))
        gpt_jedro = gpt_result['jedro']
        
        gpt_sklep_results = json.loads(call_gpt_json(prompt_core_sklep, input))
        gpt_jedro_skep = gpt_sklep_results['jedro']
        
        input = "<jedro>" + gpt_jedro + "</jedro>" + input
        gpt_verbatim_results = json.loads(call_gpt_json(prompt_find_verbatim, input))
        gpt_verbatim = gpt_verbatim_results['podlaga']

        gpt_verbatim_sklep_results = json.loads(call_gpt_json(prompt_find_verbatim_sklep, input))
        gpt_verbatim_sklep = gpt_verbatim_sklep_results['podlaga']


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
            "gpt_result_improved": {
                "gpt_jedro": gpt_jedro_skep,
                "gpt_verbatim": gpt_verbatim_sklep
            },
        }
        results.append(results_dict)
    
    adjusted_results = {'prompt_core': prompt_core, "prompt_find_verbatim": prompt_find_verbatim, 'prompt_core_improved': prompt_core_improved, "prompt_find_verbatim_improved": prompt_find_verbatim_improved, "results": results}
    with open(result_filename, 'w', encoding='utf-8') as f:
        json.dump(adjusted_results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # result_filename = "sample_verbatim_sodba_gpt_results.json"

    # with open("data/datasets/sample_verbatim_sodba.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
        
    # process_sodba_files(data, result_filename)
    
    
    
    result_filename = "sample_verbatim_sklep_gpt_results.json"

    with open("data/datasets/sample_verbatim_sklep.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    process_sklep_files(data, result_filename)



