import os
import sys


sys.path.insert(0, './src/')

import json
from flask import Flask
from flask_cors import CORS
from flask import request

import pandas as pd

from process_data import process, read_txt, read_json

SLIDE_DATA_PATH = './slideMeta/slideData'

app = Flask(__name__)
CORS(app)   

@app.route('/get_data', methods=['POST'])
def prediction():
    decoded = request.data.decode('utf-8')
    request_json = json.loads(decoded)
    presentation_id = request_json["presentationId"]
    similarity_type = request_json["similarityType"]
    outlining_approach = request_json["outliningApproach"]
    apply_thresholding = request_json["applyThresholding"]
    apply_heuristics = request_json["applyHeuristics"]

    print(request_json)


    parent_path = os.path.join(SLIDE_DATA_PATH, str(presentation_id))
    parent_path_2 = os.path.join(SLIDE_DATA_PATH, str(presentation_id))

    paper_path = os.path.join(parent_path, 'paperData.txt')
    script_path = os.path.join(parent_path_2, 'scriptData.txt')
    section_path = os.path.join(parent_path, 'sectionData.txt')

    #data_path = os.path.join(parent_path, 'result.json')

    return json.dumps({
        "paper": read_txt(paper_path),
        "script": read_txt(script_path),
        "sections": read_txt(section_path),
        "data": process(parent_path, presentation_id, similarity_type, outlining_approach, apply_thresholding, apply_heuristics),
        "presentationId": presentation_id,
    })

@app.route('/get_evaluation_results', methods=['POST'])
def get_evaluation_result():
    result_path = os.path.join(SLIDE_DATA_PATH, 'performance.json')

    results = read_json(result_path)

    return json.dumps({
        "evaluationResults": results["evaluationResults"],
    })

app.run(host='0.0.0.0', port=3555)
