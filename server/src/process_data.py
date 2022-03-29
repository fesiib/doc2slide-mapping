import json
import os
import sys
import numpy

from string import digits

from nltk.tokenize import word_tokenize

import nltk
nltk.download('punkt')

sys.path.insert(0, '../')

from gen_similarity_table import \
    get_sentences, get_classifier_similarity,\
    get_cosine_similarity, get_keywords_similarity

from gen_outline import get_outline_generic

from evaluate_outline import evaluate_outline, evaluate_performance, GROUND_TRUTH_EXISTS

from annotation import scan_annotations, read_json

from slides_segmentation import get_slides_segmentation

from __init__ import sort_section_data

SKIPPED_SECTIONS = [
    "CCS CONCEPTS",
    "KEYWORDS",
    "ACM Reference Format:",
    "REFERENCES",
    "ACKNOWLEDGMENTS"
]
MIN_PARAGRAPH_LENGTH = 10

    
def read_txt(path) :
    lines = []
    with open(path, "r") as f:
        while True :
            line = f.readline()
            if not line :
                break
            lines.append(line.strip())
    return lines  

def is_section_skipped(section):
    for skipped_section in SKIPPED_SECTIONS:
        if skipped_section in section:
            return True
    return False

def add_sections_as_paragraphs(section_data, paper_data):
    ret_section_data = []
    ret_paper_data = []

    for i in range(0, len(section_data)):
        if i == 0 or section_data[i] != section_data[i - 1]:
            ret_section_data.append(section_data[i])
            ret_paper_data.append(section_data[i] + ".")
        ret_section_data.append(section_data[i])
        ret_paper_data.append(paper_data[i])
    return ret_section_data, ret_paper_data

def fix_section_titles(section_data, paper_data, paper_data_json):
    rev_mapping = {}

    def get_main_section(title):
        title_parts = title.strip().split(" ")
        if (title_parts[0] in digits) is False:
            return False
        for title_part in title_parts[1:]:
            if len(title_part) < 2: 
                continue
            elif title_part.isupper() is True or title_part in digits:
                break
            else:
                return False
        return True

    last_title = None    

    if "sections" in paper_data_json:
        for section in paper_data_json["sections"]:
            if "title" in section and "text" in section["title"]:
                title = section["title"]["text"]
                if get_main_section(title) is True:
                    last_title = title
                if last_title is not None:
                    rev_mapping[title] = last_title

    ret_section_data = []
    ret_paper_data = []
    #cnt_title = 0
            
    for (section, paragraph) in zip(section_data, paper_data):
        if is_section_skipped(section) or section not in rev_mapping:
            continue
        ret_section_data.append(rev_mapping[section])
        ret_paper_data.append(paragraph)

    return ret_section_data, ret_paper_data

def process(path, presentation_id, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics):
    timestamp = open(os.path.join(path, "frameTimestamp.txt"), "r")

    timestamp_data = []
    script_data = []

    script_data = read_txt(os.path.join(path, "scriptData.txt"))

    gt_path = os.path.join(path, "groundTruth.json")
    gt_data = {
        'groundTruthSegments': [],
    }
    if (os.path.isfile(gt_path)):
        gt_data = read_json(gt_path)

    meta_info = {
        "keywords": ["empty"],
        "title": ["empty"],
        "authors": ["empty"],
    }
    if os.path.isfile(os.path.join(path, "keywords.json")):
        new_meta_info = read_json(os.path.join(path, "keywords.json"))
        for key in meta_info.keys():
            if key in new_meta_info:
                meta_info[key] = new_meta_info[key]

    while True :
        line = timestamp.readline()
        if not line :
            break
        start_time, end_time = float(line.split('\t')[0]), float(line.split('\t')[1])
        timestamp_data.append([start_time, end_time])

    ocr_data = []
    for i in range(len(timestamp_data)) :
        ocr_file_path = os.path.join(path, "ocr", str(i) + ".jpg.txt")
        ocr_data.append('')
        try:
            with open(ocr_file_path, "r") as (ocr_file, err):
                if err:
                    print(err)
                first_line = False
                while True :
                    line = ocr_file.readline()
                    if not line :
                        break
                    if first_line is True:
                        first_line = False
                        continue
                    res = line.split('\t')[-1].strip()
                    if len(res) > 0 :
                        ocr_data[-1] = ocr_data[-1] + ' ' + res
        except:
            continue
    result = {}

    slide_info = []
    start_time_stamp = 0
    for i in range(len(timestamp_data)):
        end_time_stamp = timestamp_data[i][1]

        # if i > 1:
        #     if (start_time_stamp - slide_info[1]["startTime"]) >= 16 * 60:
        #         break
        #     if (end_time_stamp - slide_info[1]["startTime"]) >= 16 * 60:
        #         end_time_stamp = slide_info[1]["startTime"] + (16 * 60) + 1

        slide_info.append({
            "index": i,
            "startTime": start_time_stamp,
            "endTime": end_time_stamp,
            "script": script_data[i],
            "ocrResult": ocr_data[i],
        })
        start_time_stamp = end_time_stamp

    result['slideInfo'] = slide_info   
    result['slideCnt'] = len(slide_info)
    result['metaInfo'] = meta_info
    result['groundTruthOutline'] = gt_data['groundTruthSegments']

    # if presentation_id < 100000:
    #     return result

    paper_data_json = read_json(os.path.join(path, "paperData.json"))
    paper_data = read_txt(os.path.join(path, "paperData.txt"))
    section_data = read_txt(os.path.join(path, "sectionData.txt"))
    annotations = scan_annotations(os.path.join(path, "annotations"))

    section_data, paper_data = add_sections_as_paragraphs(section_data, paper_data)

    section_data, paper_data = fix_section_titles(section_data, paper_data, paper_data_json)

    slides_segmentation = get_slides_segmentation(path, slide_info)

    #result['title'] = "tempTitle"
    result['annotations'] = annotations
    result['sectionTitles'] = sort_section_data(section_data)
    result['slidesSegmentation'] = slides_segmentation

    _paper_data = []
    _script_data = []

    script_sentence_range = []
    for i in range(len(slide_info)):
        script = slide_info[i]["script"]
        ocr = slide_info[i]["ocrResult"]
        sentences = []
        # if (len(ret_script_data) > 10):
        #     break
        if i == 0 or i == len(slide_info) - 1:
            sentences = [""]
        elif (similarity_type == "classifier"):
            sentences = [script + " " + ocr]
        else:
            sentences = get_sentences(script)
            sentences.append(ocr)
        script_sentence_range.append(len(sentences))
        _script_data.extend(sentences)

    paper_sentence_id = []
    for i, paragraph in enumerate(paper_data):
        if (len(word_tokenize(paragraph)) < MIN_PARAGRAPH_LENGTH):
            continue
        sentences = get_sentences(paragraph)
        for j in range(len(_paper_data), len(sentences) + len(_paper_data)):
            paper_sentence_id.append(i)
        _paper_data.extend(sentences)

    print("Sentences# {} Paragraphs# {}".format(len(_paper_data), len(paper_data)))
    print("Sentences# {} Scripts# {}".format(len(_script_data), len(slide_info)))

    if similarity_type == 'keywords':
        overall, top_sections, paper_keywords, script_keywords = get_keywords_similarity(similarity_method,
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, apply_heuristics, slide_info, section_data, top_sections, slides_segmentation)

        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = script_keywords
        result["paperSentences"] = paper_keywords
    elif similarity_type == 'cosine':
        overall, top_sections = get_cosine_similarity(similarity_method,
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, apply_heuristics, slide_info, section_data, top_sections, slides_segmentation)

        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = _script_data
        result["paperSentences"] = _paper_data
    elif similarity_type == "classifier":
        overall, top_sections, paper_data_by_section = get_classifier_similarity(similarity_method,
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, apply_heuristics, slide_info, section_data, top_sections, slides_segmentation)
        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = paper_data_by_section
        result["paperSentences"] = _script_data

    result["evaluationData"] = {
        "groundTruth": 
            evaluate_outline(result["outline"], result["groundTruthOutline"], result["slideInfo"], result["topSections"]),
    }
    for ground_truth_id, ground_truth_outline in annotations.items():
        result["evaluationData"][ground_truth_id] = evaluate_outline(
            result["outline"], ground_truth_outline, result["slideInfo"], result["topSections"]
        )

    apply_thresholding_str = "T1"
    if apply_thresholding is False:
        apply_thresholding_str = "T0"

    apply_heuristics_str = "H1"
    if apply_heuristics:    
        apply_heuristics_str = "H0"

    resultname = "result_" + \
        similarity_type + "_" + similarity_method + "_" + outlining_approach + "_" + \
        apply_thresholding_str + "_" + apply_heuristics_str + ".json"

    os.makedirs(os.path.join(path, "results"), exist_ok=True)

    with open(os.path.join(path, "results", resultname), "w") as f:
        f.write(json.dumps(result))
    with open(os.path.join(path, "result.json"), "w") as f:
        f.write(json.dumps(result))
    return result

def evaluate_model(parent_path, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics):
    evaluations = []

    for id in GROUND_TRUTH_EXISTS:
        path = parent_path + str(id)
        print(f'Testing: id={id} similarity={similarity_type} method={similarity_method} outlining={outlining_approach} thresholding={apply_thresholding} heuristics={apply_heuristics}')
        output = process(path, id, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics)
        evaluations.append(output["evaluationData"])

    return evaluate_performance(evaluations, GROUND_TRUTH_EXISTS)

def evaluate_all_models():
    similarity_types = ["keywords", "classifier", "cosine"]
    similarity_methods = ["tf-idf", "embedding"]
    #outlining_approaches = ["dp_mask", "dp_simple", "simple"]
    outlining_approaches = ["dp_mask"]
    thresholdings = [False, True]
    heuristics = [False, True]

    results = []

    with open("./slideMeta/slideData/performance.json", "w") as f:
        for similarity_type in similarity_types:
            for similarity_method in similarity_methods:
                if similarity_type == 'keywords':
                    if similarity_method != 'tf-idf':
                        continue
                for outlining_approach in outlining_approaches:
                    for apply_thresholding in thresholdings:
                        for apply_heuristics in heuristics:
                            output = evaluate_model('slideMeta/slideData/', similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics)
                            json_output = {
                                "modelConfig": {
                                    "similarityType": similarity_type,
                                    "similarityMethod": similarity_method,
                                    "outliningApproach": outlining_approach,
                                    "applyThresholding": apply_thresholding,
                                    "applyHeuristics": apply_heuristics,
                                },
                                "result": output
                            }
                            results.append(json_output)
        json.dump({
            "evaluationResults": results
        }, fp=f, indent=2)

if __name__ == "__main__":

    #evaluate_all_models()

    #output = evaluate_model('slideMeta/slideData/', similarity_type="classifier", outlining_approach="dp_simple", apply_thresholding=True)

    #print(json.dumps(output, indent=4))

    output = process('slideMeta/slideData/13', 13, similarity_type="classifier", similarity_method="tf-idf", outlining_approach="dp_mask", apply_thresholding=False, apply_heuristics=True)
    #print(output["outline"])
    print(json.dumps(output["outline"], indent=2))