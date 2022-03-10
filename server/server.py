import os
import sys


sys.path.insert(0, './src/')

import json
from flask import Flask
from flask_cors import CORS
from flask import request, send_file

import pandas as pd

from process_data import process, read_txt
from annotation import read_json

from pathlib import Path

SLIDE_DATA_PATH = './slideMeta/slideData'

app = Flask(__name__)
CORS(app)

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
    return {
        "slideCnt": data["slideCnt"],
        "metaInfo": data["metaInfo"],
        "slideInfo": data["slideInfo"],
        "outline": data["outline"],
        "sectionTitles": data["sectionTitles"],
        "evaluationData": data["evaluationData"]
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
    parent_path_2 = os.path.join(SLIDE_DATA_PATH, str(presentation_id))

    paper_path = os.path.join(parent_path, 'paperData.txt')
    script_path = os.path.join(parent_path_2, 'scriptData.txt')
    section_path = os.path.join(parent_path, 'sectionData.txt')

    #data_path = os.path.join(parent_path, 'result.json')

    return {
        "paper": read_txt(paper_path),
        "script": read_txt(script_path),
        "sections": read_txt(section_path),
        "data": process(parent_path, presentation_id, similarity_type, similarity_method, outlining_approach, apply_thresholding, apply_heuristics),
        "presentationId": presentation_id,
    }

def __presentation_data(presentation_id):
    similarity_type = "classifier"
    similarity_method = "tf-idf"
    outlining_approach = "dp_mask"
    apply_thresholding = False
    apply_heuristics = True

    data = None

    parent_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id))    
    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")
    summary = read_json(summary_path)

    if presentation_id in summary["valid_presentation_index"]:
        result_path = os.path.join(parent_path, "result.json")
        if os.path.isfile(result_path) is True:
            data = read_json(result_path)
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

    if presentation_id in summary["valid_presentation_index"]:
        result_path = os.path.join(parent_path, "results", resultname)
        if os.path.isfile(result_path) is True:
            data = read_json(result_path)
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

    presentations_data = read_csv("./data.csv")

    return json.dumps({
        "summaryData": summary,
        "presentationData": presentations_data,
    })


@app.route('/mapping/all_data', methods=['POST'])
def all_data():
    summary_path = os.path.join(SLIDE_DATA_PATH, "summary.json")
    summary = read_json(summary_path)

    valid_presentation_ids = summary["valid_presentation_index"]

    all_data = []

    for presentation_id in valid_presentation_ids:
        data = __presentation_data(presentation_id)
        all_data.append({
            "presentationId": presentation_id,
            "data": __filter_data(data),
        })
    
    return json.dumps({
        "allData": all_data,
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
    return send_file(image_path, mimetype='image/jpg')

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

app.run(host='0.0.0.0', port=7777)
