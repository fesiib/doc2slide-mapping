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
    get_cosine_similarity, get_keywords_similarity, get_strong_similarity

from gen_outline import get_outline_generic

from evaluate_outline import evaluate_outline, evaluate_performance, GROUND_TRUTH_EXISTS

from annotation import scan_annotations, read_json

from slides_segmentation import get_slides_segmentation

from __init__ import sort_section_data, SECTION_TITLE_MARKER

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

def store_processed_paper_data(path, section_data, paper_data):
    with open(os.path.join(path, "processedPaperData.json"), "w") as f:
        json.dump({
            "sectionData": section_data,
            "paperData": paper_data,
        }, fp=f, indent=2)

def get_all_processed_paper_data(parent_path, cur_presentation_id):
    section_data = []
    paper_data = []
    for presentation_id in os.listdir(parent_path):
        path = os.path.join(parent_path, presentation_id, "processedPaperData.json")
        if os.path.isfile(path) is False:
            continue
        if int(presentation_id) == cur_presentation_id:
            continue
        with open(path, "r") as f:
            json_obj = json.load(f)
            section_data.extend(json_obj["sectionData"])
            paper_data.extend(json_obj["paperData"])
    return section_data, paper_data

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
            ret_paper_data.append(SECTION_TITLE_MARKER + section_data[i] + ".")

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

    ### Section-level
    # all_paragraphs_per_section = {}

    # for (section, paragraph) in zip(ret_section_data, ret_paper_data):
    #     if section not in all_paragraphs_per_section:
    #         all_paragraphs_per_section[section] = ""
    #     all_paragraphs_per_section[section] += " " + paragraph
    
    # ret_section_data = []
    # ret_paper_data = []

    # ret_section_data = list(all_paragraphs_per_section.keys())
    # ret_paper_data = list(all_paragraphs_per_section.values())

    return ret_section_data, ret_paper_data

def shrink_slide_info(slide_info, transitions):
    shrunk_slide_info = [{
        "index": 0,
        "left": 0,
        "right": 0,
        "startTime": slide_info[0]["startTime"],
        "endTime": slide_info[0]["endTime"],
        "script": slide_info[0]["script"],
        "ocrResult": slide_info[0]["ocrResult"],
    }]
    start_slide = 1
    for idx in transitions:
        script = ""
        for k in range(start_slide, idx + 1):
            script += slide_info[k]["script"]
        shrunk_slide_info.append({
                "index": idx,
                "left": start_slide,
                "right": idx,
                "startTime": slide_info[start_slide]["startTime"],
                "endTime": slide_info[idx]["endTime"],
                "script": script,
                "ocrResult": slide_info[idx]["ocrResult"],
        })
        start_slide = idx + 1
    return shrunk_slide_info

def expand_top_sections(top_sections, shrunk_slide_info):
    expanded_top_sections = []
    for i, slide in enumerate(shrunk_slide_info):
        for j in range(slide["left"], slide["right"] + 1):
            expanded_top_sections.append(top_sections[i])
    return expanded_top_sections

def process(path, presentation_id, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics):
    parent_path = '/'.join(path.split('/')[:-1])
    freq_words_per_section = read_json(os.path.join(parent_path, "freqWordsPerSection.json"))
    
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
        ocr_file_path = os.path.join(path, "ocr", str(i) + ".json")
        ocr_data.append('')
        if os.path.isfile(ocr_file_path) is True:
            with open(ocr_file_path, "r") as f:
                ocr_results = json.load(f)
                height = ocr_results["imageSize"]["height"]
                width = ocr_results["imageSize"]["width"]

                processed_ocr = []

                for ocr_result in ocr_results["ocrResult"]:
                    text = ocr_result["text"]
                    conf = ocr_result["conf"]
                    bboxes = ocr_result["boundingBox"]
                    x1 = width + 1
                    x2 = -1
                    y1 = height + 1
                    y2 = -1
                    for bbox in bboxes:
                        x1 = min(x1, bbox[0])
                        x2 = max(x2, bbox[0])
                        y1 = min(y1, bbox[1])
                        y2 = max(y2, bbox[1])
                    importance = conf * (x2 - x1) * (y2 - y1)
                    processed_ocr.append((text, importance))
                
                for ocr_result in processed_ocr:
                    ocr_data[-1] += ocr_result[0] + " "
                #ocr_data[-1] += "."
                
    result = {}

    slide_info = []
    start_time_stamp = 0
    for i in range(len(timestamp_data)):
        end_time_stamp = timestamp_data[i][1]
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

    paper_data_json = read_json(os.path.join(path, "paperData.json"))
    paper_data = read_txt(os.path.join(path, "paperData.txt"))
    section_data = read_txt(os.path.join(path, "sectionData.txt"))
    annotations = scan_annotations(os.path.join(path, "annotations"))

    section_data, paper_data = add_sections_as_paragraphs(section_data, paper_data)

    section_data, paper_data = fix_section_titles(section_data, paper_data, paper_data_json)

    store_processed_paper_data(path, section_data, paper_data)

    slides_segmentation = get_slides_segmentation(path, slide_info)

    #result['title'] = "tempTitle"
    result['annotations'] = annotations
    result['sectionTitles'] = sort_section_data(section_data)
    result['slidesSegmentation'] = slides_segmentation

    transitions = []
    for slides_segment in slides_segmentation:
        if slides_segment['endSlideIndex'] < 1:
            continue
        transitions.append(slides_segment['endSlideIndex'])

    print(transitions)

    shrunk_slide_info = shrink_slide_info(slide_info, transitions)

    _coarse_paper_data = []
    _coarse_script_data = []

    _paper_data = []
    _script_data = []

    coarse_script_sentence_range = []
    script_sentence_range = []
    for i in range(len(shrunk_slide_info)):
        script = shrunk_slide_info[i]["script"]
        ocr = shrunk_slide_info[i]["ocrResult"]
        sentences = []
        if i == 0 or i == len(shrunk_slide_info) - 1:
            sentences = [""]
        elif (similarity_type == "classifier"):
            sentences = [script + " " + ocr]
        else:
            sentences = get_sentences(script)
            sentences.append(ocr)
        script_sentence_range.append(len(sentences))
        _script_data.extend(sentences)

        coarse_sentences = []
        if i == 0 or i == len(shrunk_slide_info) - 1:
            coarse_sentences = [""]
        else:
            coarse_sentences = [script + " " + ocr]
        coarse_script_sentence_range.append(len(coarse_sentences))
        _coarse_script_data.extend(coarse_sentences)

    coarse_paper_sentence_id = []
    paper_sentence_id = []
    for i, paragraph in enumerate(paper_data):
        if (len(word_tokenize(paragraph)) < MIN_PARAGRAPH_LENGTH):
            if paragraph.startswith(SECTION_TITLE_MARKER) is False:
                continue
        sentences = get_sentences(paragraph)
        for j in range(len(_paper_data), len(sentences) + len(_paper_data)):
            paper_sentence_id.append(i)
        _paper_data.extend(sentences)

        coarse_sentences = [paragraph]
        for j in range(len(_coarse_paper_data), len(coarse_sentences) + len(_coarse_paper_data)):
            coarse_paper_sentence_id.append(i)
        _coarse_paper_data.extend(sentences)

    
    
    # other_section_data, other_paper_data = get_all_processed_paper_data(parent_path, presentation_id)

    # for i, paragraph in enumerate(other_paper_data):
    #     if (len(word_tokenize(paragraph)) < MIN_PARAGRAPH_LENGTH):
    #         continue
    #     #sentences = get_sentences(paragraph)
    #     sentences = [paragraph]
    #     _paper_data.extend(sentences)
    # print("Sentences# {} Paragraphs# {} Other# {}".format(len(_paper_data), len(paper_data), len(other_paper_data)))
    

    print("Sentences# {} Paragraphs# {}".format(len(_paper_data), len(paper_data)))
    print("Sentences# {} Scripts# {}".format(len(_script_data), len(shrunk_slide_info)))


    print("Coarse Sentences# {} Paragraphs# {}".format(len(_coarse_paper_data), len(paper_data)))
    print("Coarse Sentences# {} Scripts# {}".format(len(_coarse_script_data), len(shrunk_slide_info)))

    if similarity_type == 'keywords':
        overall, top_sections, paper_keywords, script_keywords = get_keywords_similarity(similarity_method,
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range,
            freq_words_per_section,
            apply_thresholding
        )
        outline, weights = get_outline_generic(
            outlining_approach,
            apply_heuristics,
            shrunk_slide_info,
            section_data,
            top_sections,
            transitions
        )
        expanded_top_sections = expand_top_sections(top_sections, shrunk_slide_info)
        result['topSections'] = expanded_top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = script_keywords
        result["paperSentences"] = paper_keywords
    elif similarity_type == 'strong':
        overall, top_sections, paper_keywords, script_keywords = get_strong_similarity(similarity_method,
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, transitions,
            freq_words_per_section
        )
        outline, weights = get_outline_generic(
            outlining_approach,
            apply_heuristics,
            shrunk_slide_info,
            section_data,
            top_sections,
            transitions
        )

        expanded_top_sections = expand_top_sections(top_sections, shrunk_slide_info)
        print(len(top_sections), len(expanded_top_sections))
        result['topSections'] = expanded_top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = script_keywords
        result["paperSentences"] = paper_keywords
    elif similarity_type == 'cosine':
        overall, top_sections = get_cosine_similarity(similarity_method,
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range,
            freq_words_per_section,
            apply_thresholding
        )

        # coarse_overall, coarse_top_sections = get_cosine_similarity(similarity_method,
        #     _coarse_paper_data, _coarse_script_data, section_data, coarse_paper_sentence_id, coarse_script_sentence_range,
        #     freq_words_per_section,
        #     apply_thresholding
        # )

        outline, weights = get_outline_generic(
            outlining_approach,
            apply_heuristics,
            shrunk_slide_info,
            section_data,
            top_sections,
            transitions,
            coarse_top_sections=[]
        )

        expanded_top_sections = expand_top_sections(top_sections, shrunk_slide_info)
        #expaned_coarse_top_sections = expand_top_sections(coarse_top_sections, shrunk_slide_info)
        result['topSections'] = expanded_top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = _script_data
        result["paperSentences"] = _paper_data
    elif similarity_type == "classifier":
        overall, top_sections, paper_data_by_section = get_classifier_similarity(similarity_method,
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range,
            freq_words_per_section,
            apply_thresholding,
        )
        outline, weights = get_outline_generic(
            outlining_approach,
            apply_heuristics,
            shrunk_slide_info,
            section_data,
            top_sections,
            transitions
        )
        
        expanded_top_sections = expand_top_sections(top_sections, shrunk_slide_info)
        result['topSections'] = expanded_top_sections
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

    #output = process('slideMeta/slideData/90', 90, similarity_type="cosine", similarity_method="embedding", outlining_approach="strong", apply_thresholding=False, apply_heuristics=True)
    #output = process('slideMeta/slideData/13', 13, similarity_type="strong", similarity_method="tf-idf", outlining_approach="strong", apply_thresholding=False, apply_heuristics=False)
    #output = process('slideMeta/slideData/477', 477, similarity_type="cosine", similarity_method="tf-idf", outlining_approach="strong", apply_thresholding=False, apply_heuristics=False)
    output = process('slideMeta/slideData/689', 689, similarity_type="cosine", similarity_method="tf-idf", outlining_approach="strong", apply_thresholding=False, apply_heuristics=False)
    #output = process('slideMeta/slideData/477', 477, similarity_type="strong", similarity_method="tf-idf", outlining_approach="strong", apply_thresholding=False, apply_heuristics=False)
    
    #output = process('slideMeta/slideData/106', 106, similarity_type="cosine", similarity_method="tf-idf", outlining_approach="strong", apply_thresholding=False, apply_heuristics=False)
    

    print(json.dumps(output["outline"], indent=2))
    print(json.dumps(output["evaluationData"]["groundTruth"], indent=2))