from gpt_utils import call_gpt_json
import json

prompt_compare_legal_cores = """Podani sta dve pravni jedri sodbe. Tvoja naloga je, da preveriš, ali vsebujeta enake informacije.

### Navodila:
1. **Primerjaj vsebinsko enakost**: Preveri, ali obe jedri izražata isti pravni zaključek, čeprav sta lahko zapisani drugače.
2. **Če se ujemata**, vrni naslednji JSON:
   ```json
   {"identicno": true, "razlike":{"jedro_1_manjkajoce_info": [], "jedro_2_manjkajoce_info": []}}
   
3.	Če ne vsebujeta enakih informacij, identificiraj razlike:
    - Informacije, ki so prisotne le v prvem jedru.
    - Informacije, ki so prisotne le v drugem jedru.
    - Razlike navedi v obliki kratkih ključnih besed ali fraz, ki povzema manjkajoče informacije.

Pričakovan JSON izhod:
{
   "identicno": false,
   "razlike": {
      "jedro_1_manjkajoce_info": ["ključna informacija 1", "ključna informacija 2"],
      "jedro_2_manjkajoce_info": ["ključna informacija 3", "ključna informacija 4"]
   }
}

Pomembno:
	•	Ne primerjaj zgolj po besedilu, ampak po pomenski vsebini.
	•	Osredotoči se le na pravni pomen in ne na slogovne razlike.
	•	Ključne fraze morajo biti čim bolj jedrnate in zajeti bistvene pravne informacije.
	•	Če razlike niso bistvene (gre le za slogovne spremembe), kljub temu označi, da sta jedri enaki.
"""

def process_cores(core_results: list[dict]):

    for i,core_result in enumerate(core_results['results']):
        print(i+1)
        

        jedro_gpt = core_result['gpt_result']['gpt_jedro']
        jedro_original = core_result['original']['jedro']

        jedro1 = jedro_gpt
        jedro2 = jedro_original

        input = "<jedro1>" + jedro1 + "</jedro1>" + "\n\n <jedro2>" + jedro2 + "</jedro2>"
        LLM_eval_result = json.loads(call_gpt_json(prompt_compare_legal_cores, input))

        # Nočem da LLM ve katero jedro je bilo gpt generated, da ne bo biasa, zato tam anonimiziran na jedro 1/2
        LLM_eval_result["razlike"]["jedro_gpt_manjkajoce_info"] = LLM_eval_result["razlike"].pop("jedro_1_manjkajoce_info")
        LLM_eval_result["razlike"]["jedro_original_manjkajoce_info"] = LLM_eval_result["razlike"].pop("jedro_2_manjkajoce_info")
        
        core_result["LLM_eval_result"]  = LLM_eval_result



if __name__ == "__main__":
    
    input_filename = "results_2step_core_verbatim_2.json"
    with open(input_filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    process_cores(data)

    output_filename = input_filename.replace('.json', '_w_llm_evals.json')
    with open(input_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii= False, indent=4)
