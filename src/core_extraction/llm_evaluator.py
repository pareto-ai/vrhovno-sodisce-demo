from gpt_utils import call_gpt_json
import json

def compare_legal_cores(jedro1, jedro2):
    """Compare two legal cores and return differences."""
    prompt = """Podani sta dve pravni jedri sodbe. Tvoja naloga je, da preveriš, ali vsebujeta enake informacije.

    Navodila:
    1. Primerjaj vsebinsko enakost: Preveri, ali obe jedri izražata isti pravni zaključek, čeprav sta lahko zapisani drugače.
    2. Če se ujemata, vrni naslednji JSON:
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

    input_text = f"<jedro1>{jedro1}</jedro1>\n\n<jedro2>{jedro2}</jedro2>"
    result = json.loads(call_gpt_json(prompt, input_text))
    
    # Nočem da LLM ve katero jedro je bilo gpt generated, da ne bo biasa, zato tam anonimiziran na jedro 1/2, tukaj pa naredim distinktno
    result["razlike"]["jedro_1_manjkajoce_info"] = result["razlike"].pop("jedro_1_manjkajoce_info")
    result["razlike"]["jedro_2_manjkajoce_info"] = result["razlike"].pop("jedro_2_manjkajoce_info")
    
    return result


def reword_core(sodba, jedro):
    """Reword a legal core while maintaining the same legal meaning."""
    prompt = """Podana ti je sodba (<sodba></sodba>) in jedro (<jedro></jedro>) te sodbe. Tvoja naloga je, da preoblikuješ jedro v drugo besedno obliko, vendar mora ohraniti popolnoma enak pravni pomen.

    Navodila:
    1. Preoblikuj jedro tako, da je zapisano drugače, vendar ohranja enako pravno vsebino.
    2. Ne dodajaj ali izpuščaj nobenih informacij – pravni pomen se ne sme spremeniti.
    3. Uporabljaj drugačne besede, sinonomizacijo in prestrukturiranje stavkov.
    4. Če obstajajo pravni izrazi, jih lahko nadomestiš z enakovrednimi izrazi, a jih ne smeš odstraniti.
    5. Vrni odgovor v obliki JSON:
    
    ```json
    {
    "reworded_jedro": "<preoblikovano_jedro>"
    }
    """
    
    input_text = f"<sodba>{sodba}</sodba>\n\n<jedro>{jedro}</jedro>"
    return json.loads(call_gpt_json(prompt, input_text))['reworded_jedro']


def expand_core(sodba, jedro):
    """Expand a legal core with one additional important legal information."""
    prompt = """Podana ti je sodba (<sodba></sodba>) in jedro (<jedro></jedro>) te sodbe. Tvoja naloga je, da jedru dodaš eno dodatno pravno informacijo, ki je pomembna in vsebovana v sodbi.
    
    Navodila:
    1.	Preberi sodbo in ugotovi vse ključne informacije.
    2.	Identificiraj eno dodatno pomembno informacijo, ki ni vključena v prvotno jedro.
    3.	Dodaj to informacijo v jedro, tako da se pravni pomen razširi, vendar ostane skladen s sodbo.
    4.	Ne spreminjaj ali odstranjuj obstoječih informacij, temveč zgolj dopolni jedro.
    5.	Vrni odgovor v obliki JSON:
    {
    "modified_jedro": "<spremenjeno_jedro_z_dodano_info>",
    "added_information": "<kratka_povzetek_dodane_info>"
    }
    """
    
    input_text = f"<sodba>{sodba}</sodba>\n\n<jedro>{jedro}</jedro>"
    result = json.loads(call_gpt_json(prompt, input_text))
    return result['modified_jedro'], result['added_information']


def create_eval_dataset(input_data):
    """Create evaluation dataset with reworded and expanded cores."""
    print("Started creating eval dataset")
    eval_dataset = []
    
    for item in input_data:
        jedro = item['jedro']
        sodba = item['obrazložitev']
        
        reworded = reword_core(sodba, jedro)
        
        expanded, added_info = expand_core(sodba, reworded)
        
        eval_dataset.append({
            'original': jedro,
            'reworded': reworded,
            'expanded': expanded,
            'added_info': added_info,
            'sodba': sodba
        })
        print("Entry added to eval dataset")
    
    return eval_dataset


def validate_llm_evaluator(eval_dataset):
    """Validate the LLM evaluator using the evaluation dataset."""
    print("Started validation of LLM eval")
    
    results = {
        'original_vs_reworded': [],
        'original_vs_expanded': []
    }
    
    metrics = {
        'original_vs_reworded': {
            'total': 0, 
            'correct': 0, 
            'expected_identical': True
        },
        'original_vs_expanded': {
            'total': 0, 
            'correct': 0, 
            'expected_identical': False
        },
    }
    
    for i, item in enumerate(eval_dataset):
        print(f"Validating item {i+1}/{len(eval_dataset)}")
        
        # Compare original vs reworded (should be identical in meaning)
        original_vs_reworded = compare_legal_cores(item['original'], item['reworded'])
        results['original_vs_reworded'].append(original_vs_reworded)
        
        metrics['original_vs_reworded']['total'] += 1
        if original_vs_reworded['identicno'] == metrics['original_vs_reworded']['expected_identical']:
            metrics['original_vs_reworded']['correct'] += 1
        
        # Compare original vs expanded (should NOT be identical in meaning)
        original_vs_expanded = compare_legal_cores(item['original'], item['expanded'])
        original_vs_expanded['eval_added_info'] = item['added_info']

        results['original_vs_expanded'].append(original_vs_expanded)
        
        metrics['original_vs_expanded']['total'] += 1
        if original_vs_expanded['identicno'] == metrics['original_vs_expanded']['expected_identical']:
            metrics['original_vs_expanded']['correct'] += 1
        
    for key in metrics:
        if metrics[key]['total'] > 0:
            metrics[key]['accuracy'] = (metrics[key]['correct'] / metrics[key]['total']) * 100
        else:
            metrics[key]['accuracy'] = 0
    
    return {
        'detailed_results': results,
        'metrics': metrics
    }

def process_cores(data):
    """Process and evaluate generated cores against original cores."""
    for i, core_result in enumerate(data['results']):
        print(f"Processing core {i+1}")
        
        jedro_gpt = core_result['gpt_result']['gpt_jedro']
        jedro_original = core_result['original']['jedro']
        
        eval_result = compare_legal_cores(jedro_gpt, jedro_original)
        
        eval_result["razlike"]["jedro_gpt_manjkajoce_info"] = eval_result["razlike"].pop("jedro_1_manjkajoce_info")
        eval_result["razlike"]["jedro_original_manjkajoce_info"] = eval_result["razlike"].pop("jedro_2_manjkajoce_info")
        
        core_result["LLM_eval_result"] = eval_result
    
    return data


def _create_eval_dataset():
    
    sample_path = "data/datasets/sample_train_verbatim2.json"
    with open(sample_path, "r", encoding="utf-8") as f:
        sample_data =  json.load(f)
    
    eval_dataset = create_eval_dataset(sample_data[:10])
    
    eval_path = "data/datasets/eval_dataset.json"
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_dataset, f, ensure_ascii=False, indent=4)


def _evaluate_LLM_evaluator():
    
    eval_path = "data/datasets/eval_dataset.json"
    with open(eval_path, "r", encoding="utf-8") as f:
        eval_dataset =  json.load(f)
    
    LLM_eval_results = validate_llm_evaluator(eval_dataset)
    eval_results_path = "data/evals/eval_results_dataset.json"
    with open(eval_results_path, "w", encoding="utf-8") as f:
        json.dump(LLM_eval_results, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    _evaluate_LLM_evaluator()

    
    # # Process and evaluate actuall data
    # results_path = "results_2step_core_verbatim_2.json"
    # with open(results_path, "r", encoding="utf-8") as f:
    #     results_data =  json.load(f)
    # processed_data = process_cores(results_data)
    # output_path = results_path.replace('.json', '_w_llm_evals.json')

    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(processed_data, f, ensure_ascii=False, indent=4)
