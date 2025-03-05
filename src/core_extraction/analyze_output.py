from html_output import apply_styles, save_html_to_file
import os
import json
from SS_utils import text_similarity

def analyze_output(examples, output_dir):
    """
    Analyze the output of the extraction process and save the results to a file.
    """
    # Extract the results
    for i, data in list(enumerate(examples["results"])):
        gpt_jedro = data["gpt_result"]["gpt_jedro"]
        gpt_jedro_verbatim = data["gpt_result"]["gpt_verbatim"]
        jedro = data["original"]["jedro"]
        obrazlozitev = data["original"]["obrazlozitev"]

        jedro_gt_results = text_similarity(jedro, obrazlozitev)
        jedro_results = text_similarity(". ".join(gpt_jedro_verbatim), obrazlozitev)

        path_to_output = f"./../../htmls/{output_dir}"
        os.makedirs(path_to_output, exist_ok=True)
        html_output = apply_styles(obrazlozitev, jedro_results[2], jedro_gt_results[2])
        save_html_to_file(html_output,
                          [gpt_jedro, jedro, "Prostor za metrike"],
                          path_to_output + f"/example_{i}.html")


if __name__ == "__main__":
    with open("./../../results/results_2step_core_verbatim.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    analyze_output(data, "2-step")