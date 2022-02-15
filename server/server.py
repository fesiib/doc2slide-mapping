import os

import json
from flask import Flask
from flask_cors import CORS
from flask import request

import pandas as pd

app = Flask(__name__)
CORS(app)

def readTXT(path):
    paragraphs = []
    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if line == "":
                continue
            paragraphs.append(line)
    return paragraphs

def readJSON(path):
    obj = {}
    with open(path, 'r') as f:
        encoded = f.read()
        obj = json.loads(encoded)
    return obj

SLIDE_DATA_PATH = './slideMeta/slideData'        

@app.route('/getData', methods=['POST'])
def prediction():
    decoded = request.data.decode('utf-8')
    requestJSON = json.loads(decoded)
    presentationId = requestJSON["presentationId"]

    parent_path = os.path.join(SLIDE_DATA_PATH, str(presentationId))

    paper_path = os.path.join(parent_path, 'paperData.txt')
    script_path = os.path.join(parent_path, 'scriptData.txt')
    data_path = os.path.join(parent_path, 'result.json')

    return json.dumps({
        "paper": readTXT(paper_path),
        "script": readTXT(script_path),
        "data": readJSON(data_path)
    })

app.run(host='0.0.0.0', port=3555)
