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

def fix_section_titles(section_data, paper_data):
    ret_section_data = []
    ret_paper_data = []
    #cnt_title = 0

    last_section = None

    def is_main_section(title):
        if title[0] in digits or title.isupper() is True:
            return True
        return False

    for (section, paragraph) in zip(section_data, paper_data):
        if is_section_skipped(section):
            continue
        if is_main_section(section) or last_section is None:
            ret_section_data.append(section)
            ret_paper_data.append(paragraph)
            last_section = section
        else:
            ret_section_data.append(last_section)
            ret_paper_data.append(paragraph)

    return ret_section_data, ret_paper_data

def process(path, presentation_id, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics):
    timestamp = open(os.path.join(path, "frameTimestamp.txt"), "r")

    timestamp_data = []
    script_data = []

    paper_data = read_txt(os.path.join(path, "paperData.txt"))
    section_data = read_txt(os.path.join(path, "sectionData.txt"))
    script_data = read_txt(os.path.join(path, "scriptData.txt"))

    gt_data = {
        'groundTruthSegments': [],
    }
    if (presentation_id in GROUND_TRUTH_EXISTS):
        gt_data = read_json(os.path.join(path, "groundTruth.json"))

    annotations = scan_annotations(os.path.join(path, "annotations"))

    section_data, paper_data = add_sections_as_paragraphs(section_data, paper_data)

    section_data, paper_data = fix_section_titles(section_data, paper_data)

    while True :
        line = timestamp.readline()
        if not line :
            break
        timestamp_data.append([float(line.split('\t')[0]), float(line.split('\t')[1])])

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

    result['title'] = "tempTitle"
    result['slideCnt'] = len(timestamp_data)
    result['groundTruthOutline'] = gt_data['groundTruthSegments']
    result['annotations'] = annotations

    slide_info = []
    startTimeStamp = 0
    for i in range(len(timestamp_data)) :
        slide_info.append({
            "index": i,
            "startTime": startTimeStamp,
            "endTime": timestamp_data[i][1],
            "script": script_data[i],
            "ocrResult": ocr_data[i],
        })
        startTimeStamp = timestamp_data[i][1]
    result['slideInfo'] = slide_info   


    _paper_data = []
    _script_data = []

    script_sentence_range = []
    for i, (script, ocr) in enumerate(zip(script_data, ocr_data)):
        sentences = []
        # if (len(ret_script_data) > 10):
        #     break
        if i == 0 or i == len(script_data) - 1:
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

    print("Sentences# {} Scripts# {}".format(len(_script_data), len(script_data)))
    print("Sentences# {} Paragraphs# {}".format(len(_paper_data), len(paper_data)))

    if similarity_type == 'keywords':
        overall, top_sections, paper_keywords, script_keywords = get_keywords_similarity(similarity_method,
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, apply_heuristics, slide_info, section_data, top_sections, script_sentence_range)

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
        outline, weights = get_outline_generic(outlining_approach, apply_heuristics, slide_info, section_data, top_sections, script_sentence_range)

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
        outline, weights = get_outline_generic(outlining_approach, apply_heuristics, slide_info, section_data, top_sections, script_sentence_range)
        
        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = paper_data_by_section
        result["paperSentences"] = _script_data

    result["evaluationData"] = evaluate_outline(
        result["outline"], result["groundTruthOutline"], result["slideInfo"], result["topSections"]
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

    with open(os.path.join(path, resultname), "w") as f:
        f.write(json.dumps(result))
    with open(os.path.join(path, "result.json"), "w") as f:
        f.write(json.dumps(result))
    return result

def evaluate_model(parent_path, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics):
    evaluations = []

    for id in GROUND_TRUTH_EXISTS:
        print(f'Testing: id={id} similarity={similarity_type} method={similarity_method} outlining={outlining_approach} thresholding={apply_thresholding} heuristics={apply_heuristics}')
        path = parent_path + str(id)
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

    evaluate_all_models()

    #output = evaluate_model('slideMeta/slideData/', similarity_type="classifier", outlining_approach="dp_simple", apply_thresholding=True)
    #print(json.dumps(output, indent=4))


    #output = process('slideMeta/slideData/20', 20, similarity_type="cosine", similarity_method="tf-idf", outlining_approach="dp_mask", apply_thresholding=False, apply_heuristics=True)
    #print(output["annotations"])