import json
import os
import sys
import numpy

from string import digits

from nltk.tokenize import word_tokenize

#nltk.download('punkt')

sys.path.insert(0, '../')

from gen_similarity_table import \
    get_sentences, get_similarity_classifier,\
    get_similarity_embeddings, get_similarity_keywords

from gen_outline import get_outline_generic

from evaluate_outline import evaluate_outline, evaluate_performance, GROUND_TRUTH_EXISTS

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


def read_json(path):
    obj = {}
    with open(path, 'r') as f:
        encoded = f.read()
        obj = json.loads(encoded)
    return obj     

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

def process(path, presentation_id, similarity_type, outlining_approach, apply_thresholding):
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
        gt_data = read_json(os.path.join(path, "groundTruth.txt"))

    section_data, paper_data = add_sections_as_paragraphs(section_data, paper_data)

    section_data, paper_data = fix_section_titles(section_data, paper_data)

    while True :
        line = timestamp.readline()
        if not line :
            break
        timestamp_data.append([float(line.split('\t')[0]), float(line.split('\t')[1])])

    ocr_data = []
    for i in range(len(timestamp_data)) :
        ocr_file = open(os.path.join(path, "ocr", str(i) + ".jpg.txt"), "r")
        ocr_data.append('')
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
    
    result = {}

    result['title'] = "tempTitle"
    result['slideCnt'] = len(timestamp_data)
    result['slideInfo']= []
    result['groundTruthOutline'] = gt_data['groundTruthSegments']
    for i in range(len(timestamp_data)) :
        result['slideInfo'].append({
            "index": i,
            "startTime": timestamp_data[i][0],
            "endTime": timestamp_data[i][1],
            "script": script_data[i],
            "ocrResult": ocr_data[i],
        })
    

    _paper_data = []
    _script_data = []

    script_sentence_range = []
    for i, (script, ocr) in enumerate(zip(script_data, ocr_data)):
        # if (len(ret_script_data) > 10):
        #     break
        if (similarity_type == "classifier"):
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
        # if (len(ret_paper_data) > 10):
        #     break
        sentences = get_sentences(paragraph)
        for j in range(len(_paper_data), len(sentences) + len(_paper_data)):
            paper_sentence_id.append(i)
        _paper_data.extend(sentences)

    print("Sentences# {} Scripts# {}".format(len(_script_data), len(script_data)))
    print("Sentences# {} Paragraphs# {}".format(len(_paper_data), len(paper_data)))

    if similarity_type == 'keywords':
        overall, top_sections, paper_keywords, script_keywords = get_similarity_keywords(
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, section_data, top_sections, script_sentence_range)

        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = script_keywords
        result["paperSentences"] = paper_keywords
    elif similarity_type == 'embeddings':
        overall, top_sections = get_similarity_embeddings(
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, section_data, top_sections, script_sentence_range)

        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = _script_data
        result["paperSentences"] = _paper_data
    elif similarity_type == "classifier":
        overall, top_sections, paper_data_by_section = get_similarity_classifier(
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, section_data, top_sections, script_sentence_range)
        
        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = paper_data_by_section
        result["paperSentences"] = _script_data

    result["evaluationData"] = evaluate_outline(
        result["outline"], result["groundTruthOutline"], result["slideInfo"], result["topSections"]
    )

    json_file = open(os.path.join(path, "result.json"), "w")
    json_file.write(json.dumps(result))
    return result

def evaluate_model(parent_path, similarity_type, outlining_approach, apply_thresholding):
    evaluations = []

    for id in GROUND_TRUTH_EXISTS:
        print("Evaluating: ", id)

        path = parent_path + str(id)
        output = process(path, id, similarity_type, outlining_approach, apply_thresholding)
        evaluations.append(output["evaluationData"])

    return evaluate_performance(evaluations, GROUND_TRUTH_EXISTS)

def evaluate_all_models():
    similarity_types = ["classifier", "keywords", "embeddings"]
    outlining_approaches = ["dp_mask", "dp_simple", "simple"]
    thresholdings = [False, True]

    results = []

    with open("./slideMeta/slideData/performance.json", "w") as f:
        for similarity_type in similarity_types:
            for outlining_approach in outlining_approaches:
                for apply_thresholding in thresholdings:
                    print(f'Testing Model: similarity={similarity_type}, outlining={outlining_approach} thresholding={apply_thresholding}')
                    output = evaluate_model('slideMeta/slideData/', similarity_type, outlining_approach, apply_thresholding)
                    
                    json_output = {
                        "modelConfig": {
                            "similarityType": similarity_type,
                            "outliningApproach": outlining_approach,
                            "thresholding": apply_thresholding,
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


    #output = process('slideMeta/slideData/0', 0, similarity_type="classifier", outlining_approach="dp_simple", apply_thresholding=True)
    #print(output["evaluationData"])