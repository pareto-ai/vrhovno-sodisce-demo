from html_output import apply_styles, save_html_to_file
import os
import json
from SS_utils import text_similarity

def analyze_output(examples, output_dir):
    """
    Analyze the output of the extraction process and save the results to a file.
    """
    # Extract the results
    precisions = []
    recalls = []
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
        precision, recall = overlap_statistics( gt_intervals,  gpt_intervals)
        print(f"Precision: {precision}, Recall: {recall}")
        html_output = apply_styles(obrazlozitev, gpt_intervals, gt_intervals)
        save_html_to_file(html_output,
                          [gpt_jedro, jedro, "Precision: {:.2f}, Recall: {:.2f}".format(precision, recall)],
                          path_to_output + f"/example_{i}.html")
        precisions.append(precision)
        recalls.append(recall)
    print ("Average precision: ", sum(precisions)/len(precisions))
    print ("Average recall: ", sum(recalls)/len(recalls))

def overlap_statistics(intervals_gt, intervals_gpt):
    """
    Calculate the precision and recall of the overlap between two lists of intervals.
    """

    text_covered, chars_found, total_length = formal_intersections(intervals_gt, intervals_gpt)
    # print(text_covered, chars_found, total_length)
    text_covered, chars_found, total_length = bruteforce_intersections(intervals_gt, intervals_gpt)
    # print(text_covered, chars_found, total_length)

    # Calculate the precision and recall
    recall = text_covered / total_length
    precision = text_covered / chars_found
    if precision > 1 or recall > 1:
        breakpoint()
    return precision, recall



def bruteforce_intersections(intervals_gt, intervals_gpt):
    gt_set = set()
    for (a,b) in intervals_gt:
        gt_set.update(range(a,b))
    gpt_set = set()
    for (a,b) in intervals_gpt:
        gpt_set.update(range(a,b))
    text_covered = len(gt_set.intersection(gpt_set))
    chars_found = len(gpt_set)
    total_length = len(gt_set)
    return text_covered, chars_found, total_length




def formal_intersections(intervals_gt, intervals_gpt):
    # Calculate the total length of the intervals
    total_length = sum([e - s for s, e in intervals_gt])
    # Calculate the length of the intervals that are in the second list
    chars_found = sum([e - s for s, e in intervals_gpt])
    # Calculate the length of the intervals that are in both lists
    text_covered = 0
    for (s1, e1) in intervals_gt:
        for (s2, e2) in intervals_gpt:
            if s1 <= s2 and e1 >= e2:
                text_covered += e2 - s2
            elif s1 >= s2 and e1 <= e2:
                text_covered += e1 - s1
            elif s1 <= s2 and e1 >= s2:
                text_covered += e1 - s2
            elif s1 <= e2 and e1 >= e2:
                text_covered += e2 - s1
    return text_covered, chars_found, total_length

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