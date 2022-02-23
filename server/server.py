import os

import json
from flask import Flask
from flask_cors import CORS
from flask import request

import pandas as pd

from process_data import process, read_txt, read_json

SLIDE_DATA_PATH = './slideMeta/slideData'

app = Flask(__name__)
CORS(app)   

@app.route('/getData', methods=['POST'])
def prediction():
    decoded = request.data.decode('utf-8')
    request_json = json.loads(decoded)
    presentation_id = request_json["presentationId"]
    similarity_type = request_json["similarityType"]
    outlining_approach = request_json["outliningApproach"]
    apply_thresholding = request_json["applyThresholding"]

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
        "data": process(parent_path, similarity_type, outlining_approach, apply_thresholding),
    })

app.run(host='0.0.0.0', port=3555)
