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

        gpt_intervals = make_intervals_prettier(jedro_results[2])
        gt_intervals = make_intervals_prettier(jedro_gt_results[2])
        html_output = apply_styles(obrazlozitev, gpt_intervals, gt_intervals)
        save_html_to_file(html_output,
                          [gpt_jedro, jedro, "Prostor za metrike"],
                          path_to_output + f"/example_{i}.html")



def make_intervals_prettier(intervals):

    changed = True
    while changed:
        intervals = sorted(intervals, key=lambda x: x[0])
        changed = False
        if len(intervals)<2:
            break
        for (s1, e1), (s2, e2) in zip(intervals, intervals[1:]):
            if s2 - e1 < 35:
                intervals.remove((s1, e1))
                intervals.remove((s2, e2))
                intervals.append((s1, e2))
                changed = True
                break
    intervals_final = []
    for (s, e) in intervals:
        if e-s > 35:
            intervals_final.append((s, e))

    return intervals_final



if __name__ == "__main__":
    with open("./../../results/results_2step_core_verbatim.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    analyze_output(data, "2-step")