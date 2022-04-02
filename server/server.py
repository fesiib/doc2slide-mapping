import os
import sys

from src.annotation import scan_annotations


sys.path.insert(0, './src/')

import json
import pandas as pd
from pathlib import Path

import waitress

from flask import Flask
from flask_cors import CORS
from flask import request, send_file

from process_data import process, read_txt
from annotation import read_json

SLIDE_DATA_PATH = "./slideMeta/slideData"
ZIP_SLIDE_DATA_PATH = "./slideMeta/slideData.zip"

USE_SAVED = True

app = Flask(__name__)
CORS(
    app,
    origins = ["http://server.hyungyu.com:9383", "http://localhost:3000"]
)

def read_csv(path):
    lines = []

    data = {}

    with open(path, "r") as f:
        line = f.readline()
        column_titles = line.strip().split(",")
        while True :
            line = f.readline()
            if not line :
                break
            entries = line.strip().split(",")
            id = int(entries[0])
            data[id] = {}
            for i in range(1, min(len(entries), len(column_titles))):
                column = column_titles[i]
                data[id][column] = entries[i]
    return data

def __filter_data(data):
    if data == None:
        return {
            "status": "No Such Presentation",
        }
    if "slideCnt" not in data:
        data["slideCnt"] = 0
    if "metaInfo" not in data:
        data["metaInfo"] = None
    if "slideInfo" not in data:
        data["slideInfo"] = []
    if "outline" not in data:
        data["outline"] = []
    if "sectionTitles" not in data:
        data["sectionTitles"] = []
    if "evaluationData" not in data:
        data["evaluationData"] = []
    if "slidesSegmentation" not in data:
        data["slidesSegmentation"] = []
    if "frameChanges" not in data:
        data["frameChanges"] = []
    return {
        "slideCnt": data["slideCnt"],
        "metaInfo": data["metaInfo"],
        "slideInfo": data["slideInfo"],
        "outline": data["outline"],
        "sectionTitles": data["sectionTitles"],
        "evaluationData": data["evaluationData"],
        "slidesSegmentation": data["slidesSegmentation"],
        "frameChanges": data["frameChanges"]
    }
def __process_presentation(
    presentation_id,
    similarity_type,
    similarity_method,
    outlining_approach,
    apply_thresholding,
    apply_heuristics,
):

    parent_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id))
    
    paper_path = os.path.join(parent_path, 'paperData.txt')
    script_path = os.path.join(parent_path, 'scriptData.txt')
    section_path = os.path.join(parent_path, 'sectionData.txt')

    # if presentation_id < 100000:
    #     return {
    #         "paper": [],
    #         "script": read_txt(script_path),
    #         "sections": [],
    #         "data": process(parent_path, presentation_id, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics),
    #         "presentationId": presentation_id,
    #     }

    # #data_path = os.path.join(parent_path, 'result.json')

    return {
        "paper": read_txt(paper_path),
        "script": read_txt(script_path),
        "sections": read_txt(section_path),
        "data": process(parent_path, presentation_id, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics),
        "presentationId": presentation_id,
    }

def __presentation_data(presentation_id):
    similarity_type = "cosine"
    similarity_method = "tf-idf"
    outlining_approach = "strong"
    apply_thresholding = False
    apply_heuristics = True

    data = None

    parent_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id))    
    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")
    summary = read_json(summary_path)

    if presentation_id in summary["all_presentation_index"] \
        and presentation_id not in summary["skipped_presentation_index"]:
        result_path = os.path.join(parent_path, "result.json")
        if os.path.isfile(result_path) is True and USE_SAVED:
            data = read_json(result_path)
            data["annotations"] = scan_annotations(os.path.join(parent_path, "annotations"))
        else:
            data = __process_presentation(
                presentation_id,
                similarity_type,
                similarity_method,
                outlining_approach,
                apply_thresholding,
                apply_heuristics,
            )
            data = data["data"]
    return data

@app.route('/mapping/presentation_data', methods=['POST'])
def presentation_data():
    decoded = request.data.decode('utf-8')
    request_json = json.loads(decoded)
    presentation_id = request_json["presentationId"]

    print(request_json)

    data = __presentation_data(presentation_id)
    data = __filter_data(data)
    
    return json.dumps({
        "presentationId": presentation_id,
        "data": data,
    })

@app.route('/mapping/presentation_data_specific', methods=['POST'])
def presentation_data_specific():
    decoded = request.data.decode('utf-8')
    request_json = json.loads(decoded)
    presentation_id = request_json["presentationId"]
    similarity_type = request_json["similarityType"]
    similarity_method = request_json["similarityMethod"]
    outlining_approach = request_json["outliningApproach"]
    apply_thresholding = request_json["applyThresholding"]
    apply_heuristics = request_json["applyHeuristics"]

    apply_thresholding_str = "T1"
    if apply_thresholding is False:
        apply_thresholding_str = "T0"

    apply_heuristics_str = "H1"
    if apply_heuristics:    
        apply_heuristics_str = "H0"

    resultname = "result_" + \
        similarity_type + "_" + similarity_method + "_" + outlining_approach + "_" + \
        apply_thresholding_str + "_" + apply_heuristics_str + ".json"

    print(request_json)

    data = None

    parent_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id))    
    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")
    summary = read_json(summary_path)

    if presentation_id in summary["all_presentation_index"]\
        and presentation_id not in summary["skipped_presentation_index"]:
        result_path = os.path.join(parent_path, "results", resultname)
        if os.path.isfile(result_path) is True and USE_SAVED:
            data = read_json(result_path)
            data["annotations"] = scan_annotations(os.path.join(parent_path, "annotations"))
        else:
            data = __process_presentation(
                presentation_id,
                similarity_type,
                similarity_method,
                outlining_approach,
                apply_thresholding,
                apply_heuristics,
            )
            data = data["data"]
    return json.dumps({
        "presentationId": presentation_id,
        "data": data,
    })

@app.route('/mapping/summary_data', methods=['POST'])
def summary_data():
    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")

    summary = read_json(summary_path)

    #presentations_data = read_csv("./data.csv")

    return json.dumps({
        "summaryData": summary,
        #"presentationData": presentations_data,
    })


@app.route('/mapping/all_data', methods=['POST'])
def all_data():
    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")
    summary = read_json(summary_path)

    computed_presentation_index = summary["computed_presentation_index"]

    all_data = []

    for presentation_id in computed_presentation_index:
        data = __presentation_data(presentation_id)
        all_data.append({
            "presentationId": presentation_id,
            "data": __filter_data(data),
        })
    
    return json.dumps({
        "allData": all_data,
    })

@app.route('/mapping/bulk_data', methods=['POST'])
def bulk_data():
    decoded = request.data.decode('utf-8')
    request_json = json.loads(decoded)
    presentation_ids = request_json["presentationIds"]

    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")
    summary = read_json(summary_path)

    all_presentation_ids = summary["all_presentation_index"]

    bulk_data = []

    for presentation_id in presentation_ids:
        if presentation_id in all_presentation_ids:
            print("\tCURRENTLY: ", presentation_id)
            data = __presentation_data(presentation_id)
            bulk_data.append({
                "presentationId": presentation_id,
                "data": __filter_data(data),
            })
    return json.dumps({
        "bulkData": bulk_data,
    })

@app.route('/mapping/process_presentation', methods=['POST'])
def process_presentation():
    decoded = request.data.decode('utf-8')
    request_json = json.loads(decoded)
    presentation_id = request_json["presentationId"]
    similarity_type = request_json["similarityType"]
    similarity_method = request_json["similarityMethod"]
    outlining_approach = request_json["outliningApproach"]
    apply_thresholding = request_json["applyThresholding"]
    apply_heuristics = request_json["applyHeuristics"]

    print(request_json)
    return json.dumps(__process_presentation(
        presentation_id,
        similarity_type,
        similarity_method,
        outlining_approach,
        apply_thresholding,
        apply_heuristics,
    ))    

@app.route('/mapping/evaluation_results', methods=['POST'])
def evaluation_results():
    result_path = os.path.join(SLIDE_DATA_PATH, 'performance.json')

    results = read_json(result_path)

    return json.dumps({
        "evaluationResults": results["evaluationResults"],
    })

@app.route("/images/<presentation_id>/<filename>", methods=["GET"])
def get_image(presentation_id, filename):
    image_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id), "images", filename)
    print(image_path)
    return send_file(image_path, mimetype='image/jpg')

@app.route("/papers/<presentation_id>/<filename>", methods=["GET"])
def get_paper(presentation_id, filename):
    paper_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id), filename)
    return send_file(paper_path, mimetype='application/pdf')

@app.route("/annotation/get_annotation", methods=["POST"])
def get_annotation():
    decoded = request.data.decode('utf-8')
    request_json = json.loads(decoded)

    presentation_id = request_json["presentationId"]
    submission_id = request_json["submissionId"]


    filename = submission_id + ".json"
    path = Path(os.path.join(SLIDE_DATA_PATH, str(presentation_id), "annotations"))

    file_path = os.path.join(path, filename)

    if os.path.isfile(file_path) is True:
        annotation = read_json(file_path)
        outline = annotation["groundTruthSegments"]
        return json.dumps({
            "presentationId": presentation_id,
            "submissionId": submission_id,
            "outline": outline,
            "status": "success"
        })
    return json.dumps({
        "presentationId": presentation_id,
        "submissionId": submission_id,
        "status": "error"
    })

@app.route("/annotation/submit_annotation", methods=["POST"])
def submit_annotation():
    decoded = request.data.decode('utf-8')
    request_json = json.loads(decoded)
    presentation_id = request_json["presentationId"]
    submission_id = request_json["submissionId"]
    outline = request_json["outline"]

    print(presentation_id, submission_id)

    filename = submission_id + ".json"
    path = Path(os.path.join(SLIDE_DATA_PATH, str(presentation_id), "annotations"))

    path.mkdir(parents=True, exist_ok=True)

    file_path = os.path.join(path, filename)

    with open(file_path, "w") as f:
        json.dump({
            "groundTruthSegments": outline,
        }, fp=f, indent=4)
    return json.dumps({
        "status": "Recorded",
    })

@app.route("/mapping/zip_slide_data", methods=["GET"])
def zip_slide_data():
    return send_file(ZIP_SLIDE_DATA_PATH, mimetype='application/zip')

def clear_results():
    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")
    summary = read_json(summary_path)

    all_presentation_index = summary["all_presentation_index"]
    for presentation_id in all_presentation_index:
        path = os.path.join(SLIDE_DATA_PATH, str(presentation_id))
        result_path = os.path.join(path, "result.json")
        if os.path.isfile(result_path) is True:
            os.remove(result_path)
        results_folder = os.path.join(path, "results")
        if os.path.isdir(results_folder):
            for filename in os.listdir(results_folder):
                result_path = os.path.join(results_folder, filename)
                os.remove(result_path)

def fix_presentation_ids():
    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")
    summary = read_json(summary_path)

    possible_presentation_index = []
    all_presentation_index = []
    computed_presentation_index = []

    for presentation_id in summary["computed_presentation_index"]:
        computed_presentation_index.append(presentation_id)
    for presentation_id in summary["all_presentation_index"]:
        check_paper_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id), "paperData.json")
        if os.path.isfile(check_paper_path):
            all_presentation_index.append(presentation_id)
    for presentation_id in summary["possible_presentation_index"]:
        check_paper_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id), "paperData.json")
        if os.path.isfile(check_paper_path):
            possible_presentation_index.append(presentation_id)
    
    with open(summary_path, "w") as f:
        json.dump({
            "presentationCnt": len(all_presentation_index),
            "computed_presentation_index": computed_presentation_index,
            "all_presentation_index": all_presentation_index,
            "possible_presentation_index": possible_presentation_index,
        }, fp=f)

if __name__ == "__main__":
    clear_results()
    #fix_presentation_ids()
    #app.run(host='0.0.0.0', port=7777)
    waitress.serve(app, host='0.0.0.0', port=7777)
