import sys

# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('all-MiniLM-L6-v2')

###############

videoFilename = str(sys.argv[1])
scriptFilename = str(sys.argv[2])
paperFilename = str(sys.argv[3])
thisIndex = str(sys.argv[4])

script = []
scriptTime = []

import pysrt

subtitle = pysrt.open(scriptFilename)

line = ''
startTime = str(subtitle[0].start.minutes) + ',' + str(subtitle[0].start.seconds)

for i in range(len(subtitle)-1) :
    t = subtitle[i].text.strip().replace('\n', ' ').strip()

    line = line.strip() + ' ' + t

    if len(t) > 0 and t[-1] == '.' :
        script.append(line.strip())
        scriptTime.append(startTime)

        line = ''
        startTime = str(subtitle[i+1].start.minutes) + ',' + str(subtitle[i+1].start.seconds)

script_f = open("./scriptParsed/" + thisIndex + ".txt", "w")

for s in script :
    script_f.write(s + "\n")

script_f = open("./scriptTime/" + thisIndex + ".txt", "w")

for s in scriptTime :
    script_f.write(s + "\n")

#################

import spacy
import json

nlp = spacy.load('en_core_web_sm')

jsonData = json.load(open(paperFilename))

bodyText = []
sectionInfo = []

for p in jsonData['sections'] :
    sectionTitle = ''

    if 'title' in p :
        sectionTitle = p['title']['text']

    for j in range(len(p['paragraphs'])) :
#         __t = nlp(p['paragraphs'][j]['text'])
#         sentences = list(__t.sents)
#         
#         for s in sentences :
#             bodyText.append(str(s))
        
        bodyText.append(p['paragraphs'][j]['text']) # paragraph-level
        sectionInfo.append(sectionTitle)

paper_f = open("./paperParsed/" + thisIndex + ".txt", "w")

for b in bodyText:
    paper_f.write(b + "\n")

###############

paper_s = open("./sectionParsed/" + thisIndex + ".txt", "w")

for b in sectionInfo:
    paper_s.write(b + "\n")


import sklearn

l = 1

script_post = []

for i in range(len(script)-l+1) :
    script_post.append(' '.join(script[i:i+l]))
    
# script_embeddings = model.encode(script_post)
# document_embeddings = model.encode(bodyText)



################
#   
#   
#   import numpy
#   
#   threshold = 5
#   
#   post_script = []
#   
#   similarity = sklearn.metrics.pairwise.cosine_similarity(script_embeddings, document_embeddings)
#   __sim = []
#   __sim_t = []
#   
#   trans = numpy.transpose(similarity)
#   
#   for i in range(len(similarity)) :
#       top_k = numpy.argsort(similarity[i])[-threshold:]
#       prob = similarity[i][top_k[0]]
#       
#       __sim.append([val if val >= prob else 0 for idx, val in enumerate(similarity[i])])
#       
#   for i in range(len(trans)) :
#       top_k = numpy.argsort(trans[i])[-threshold:]
#       prob = trans[i][top_k[0]]
#       
#       __sim_t.append([val if val >= prob else 0 for idx, val in enumerate(trans[i])])
#       
#   __sim_t = numpy.transpose(__sim_t)
#   
#   overall = []
#   
#   for i in range(len(similarity)) :
#       overall.append([ min(__sim[i][j], __sim_t[i][j]) for j in range(len(similarity[i]))])
#       
#   #similarity = overall
#   
#   #########################
#   
#   print(similarity)
#   
#   print(len(script))
#   print(len(bodyText))
#   
#   print(similarity.shape)
#   
#   import pandas as pd
#   
#   df = pd.DataFrame(data=similarity.astype(float))
#   df.to_csv('./similarity/' + thisIndex + ".csv", sep=',', header=False, float_format='%.10f', index=False)
#   
#   
############################

import cv2
import os
import time

step = 10
frames_count = 3
cam = cv2.VideoCapture(videoFilename)

currentframe = 0
frame_per_second = cam.get(cv2.CAP_PROP_FPS)
frames_captured = 0

cur = 0

while (True):
    ret, frame = cam.read()

    start_minutes = int(scriptTime[cur].split(',')[0])
    start_seconds = int(scriptTime[cur].split(',')[1])

    finish_minutes= int(scriptTime[cur+1].split(',')[0])
    finish_seconds = int(scriptTime[cur+1].split(',')[1])

    start_final_seconds = start_minutes * 60 + start_seconds
    finish_final_seconds = finish_minutes * 60 + finish_seconds

    final_seconds = (start_final_seconds + finish_final_seconds) // 2
    frame_cnt = final_seconds * frame_per_second

    if ret:
        if currentframe > frame_cnt :
            # currentframe = 0
            name = 'frame/' + thisIndex + '/' + str(cur) + '.jpg'

            print(name)

            cv2.imwrite(name, frame[:, :len(frame[0])//2])
            cur = cur + 1

            if cur >= len(scriptTime)-1 :
                break

        currentframe += 1

    if ret==False:
        break
cam.release()
cv2.destroyAllWindows()


