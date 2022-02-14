import json
from flask import Flask
from flask_cors import CORS
from flask import request
import glob
import pandas as pd

app = Flask(__name__)
CORS(app)

def readFile(f, ext) :
    if ext == 'txt' :
        retValue = []

        while True:
            line = f.readline()
            if not line: 
                break

            retValue.append(line.strip())

        return retValue
    else :
        return pd.read_csv(f, header=None).to_numpy().tolist()

        

@app.route('/getData', methods=['POST'])
def prediction():
    paperParsedFilename = glob.glob("./paperParsed/*")
    scriptParsedFilename= glob.glob("./scriptParsed/*")
    scriptTimeFilename = glob.glob("./scriptTime/*")
    similarity = glob.glob("./similarity/*")

    print(paperParsedFilename)
    print(scriptParsedFilename)
    print(scriptTimeFilename)
    print(similarity)

    numFiles = len(paperParsedFilename)

    returnValue = []

    for i in range(1, numFiles+1) :
        paperParsedFile = open('./paperParsed/' + str(i) + '.txt')
        scriptParsedFile = open('./scriptParsed/' + str(i) + '.txt')
        scriptTimeFile = open('./scriptTime/' + str(i) + '.txt')
        similarityFile = open('./similarity/' + str(i) + '.csv')

        paperParsed = readFile(paperParsedFile, 'txt')
        scriptParsed = readFile(scriptParsedFile, 'txt')
        scriptTime = readFile(scriptTimeFile, 'txt')
        similarity = readFile('./similarity/' + str(i) + '.csv', 'csv')

        returnValue.append({
            'id': i,
            'paper': paperParsed,
            'script': scriptParsed,
            'similarity': similarity
        })


    return json.dumps(returnValue)

app.run(host='0.0.0.0', port=3555)
