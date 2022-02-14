import sys
import pandas as pd

# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer('all-MiniLM-L6-v2')

df = pd.read_csv('../data.csv')
print(df)

for index, row in df.iterrows():
    print(row) #  row['c1']

###############

# script = []
# scriptTime = []
# 
# import pysrt
# 
# subtitle = pysrt.open(scriptFilename)
# 
# line = ''
# startTime = str(subtitle[0].start.minutes) + ',' + str(subtitle[0].start.seconds)
# 
# for i in range(len(subtitle)-1) :
#     t = subtitle[i].text.strip().replace('\n', ' ').strip()
# 
#     line = line.strip() + ' ' + t
# 
#     if len(t) > 0 and t[-1] == '.' :
#         script.append(line.strip())
#         scriptTime.append(startTime)
# 
#         line = ''
#         startTime = str(subtitle[i+1].start.minutes) + ',' + str(subtitle[i+1].start.seconds)
# 
# script_f = open("./scriptParsed/" + thisIndex + ".txt", "w")
# 
# for s in script :
#     script_f.write(s + "\n")
# 
# script_f = open("./scriptTime/" + thisIndex + ".txt", "w")
# 
# for s in scriptTime :
#     script_f.write(s + "\n")
# 
# import sklearn
# 
# l = 1
# 
# script_post = []
# 
# for i in range(len(script)-l+1) :
#     script_post.append(' '.join(script[i:i+l]))
# 
# import cv2
# import os
# import time
# 
# step = 10
# frames_count = 3
# cam = cv2.VideoCapture(videoFilename)
# 
# currentframe = 0
# frame_per_second = cam.get(cv2.CAP_PROP_FPS)
# frames_captured = 0
# 
# cur = 0
# 
# while (True):
#     ret, frame = cam.read()
# 
#     start_minutes = int(scriptTime[cur].split(',')[0])
#     start_seconds = int(scriptTime[cur].split(',')[1])
# 
#     finish_minutes= int(scriptTime[cur+1].split(',')[0])
#     finish_seconds = int(scriptTime[cur+1].split(',')[1])
# 
#     start_final_seconds = start_minutes * 60 + start_seconds
#     finish_final_seconds = finish_minutes * 60 + finish_seconds
# 
#     final_seconds = (start_final_seconds + finish_final_seconds) // 2
#     frame_cnt = final_seconds * frame_per_second
# 
#     if ret:
#         if currentframe > frame_cnt :
#             # currentframe = 0
#             name = 'frame/' + thisIndex + '/' + str(cur) + '.jpg'
# 
#             print(name)
# 
#             cv2.imwrite(name, frame)
#             cur = cur + 1
# 
#             if cur >= len(scriptTime)-1 :
#                 break
# 
#         currentframe += 1
# 
#     if ret==False:
#         break
# cam.release()
# cv2.destroyAllWindows()
# 
# 
