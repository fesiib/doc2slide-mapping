import os
import json


def read_json(path):
    obj = {}
    with open(path, 'r') as f:
        encoded = f.read()
        try:
            obj = json.loads(encoded)
        except:
            obj = {}
    return obj   

def scan_annotations(path):
    if os.path.exists(path) is False:
        return {}
    annotations = {}
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            id = filename.split('.')[0]
            obj = read_json(os.path.join(path, filename))
            annotations[id] = obj["groundTruthSegments"]
    return annotations