import json
import numpy as np
import pandas as pd
import os

flag = 0 # 1 : already created, 0: newly create

dataFile = pd.read_csv("../data.csv")
cnt = 0

valid_presentation_index = []

os.system("rm -rf ./slideData/slideImages")

for index, row in dataFile.iterrows() :
    title = row['title']
    paper = str(row['paper_file'])
    video = row['video_file']
    subtitle = row['subtitle_file']
    videoURL = row['video_url']

    print(index, title, paper, video, subtitle, videoURL)
    print('')


    if paper == '' or paper == 'nan':
        continue

    valid_presentation_index.append(index)

    if flag == 0 :
        os.system("rm -rf ./slideData/" + str(index))

        os.system("cp ../" + video + " ./video.mp4")
        os.system("cp ../" + subtitle + " ./subtitle.srt")
    
        os.system("rm -rf slideImages")
 
        os.system("mkdir slideImages")


        os.system('cp ../papers/' + str(paper) + ' ../../../pdffigures2/paper.pdf')

        os.chdir('../../../pdffigures2')
        os.system('pwd')

        os.system('sbt "runMain org.allenai.pdffigures2.FigureExtractorBatchCli paper.pdf -g myPrefix"')

        os.system('cp myPrefixpaper.json ../browsingMapping/server/slideMeta/slideImages/paperData.json')
        os.chdir('../browsingMapping/server/slideMeta')





        jsonData = json.load(open('./slideImages/paperData.json'))
        
        bodyText = []
        sectionInfo = []
        
        for p in jsonData['sections'] :
            sectionTitle = ''
        
            if 'title' in p and 'text' in p['title']:
                sectionTitle = p['title']['text']
        
                for j in range(len(p['paragraphs'])) :
            #         __t = nlp(p['paragraphs'][j]['text'])
            #         sentences = list(__t.sents)
            #         
            #         for s in sentences :
            #             bodyText.append(str(s))
                    
                    bodyText.append(p['paragraphs'][j]['text']) # paragraph-level
                    sectionInfo.append(sectionTitle)
        
        paper_f = open("./slideImages/paperData.txt", "w")
        
        for b in bodyText:
            paper_f.write(b + "\n")
        
        ###############
        
        paper_s = open("./slideImages/sectionData.txt", "w")
        
        for b in sectionInfo:
            paper_s.write(b + "\n")





        os.system('cd ../browsingMapping/server')
        os.system("sh genSlides.sh")
        os.system("sh genOCR.sh")
        os.system("python getSubtitle.py")
    
        os.system("cp ../paperParsed/" + str(index+1) + ".txt ./slideImages/paperData.txt")
        os.system("cp ../sectionParsed/" + str(index+1) + ".txt ./slideImages/sectionData.txt")
    
        os.system("python genJsonStructure.py")

    

        os.system("mv slideImages slideData")
    
        os.system("mv slideData/slideImages ./slideData/" + str(index))
    elif flag == 1 :
        os.system("rm -rf slideImages")

        os.system("cp -rp ./slideData/" + str(index) + " ./slideImages")




        jsonData = json.load(open('./slideImages/paperData.json'))
        
        bodyText = []
        sectionInfo = []
        
        for p in jsonData['sections'] :
            sectionTitle = ''
        
            if 'title' in p and 'text' in p['title']:
                sectionTitle = p['title']['text']
        
                for j in range(len(p['paragraphs'])) :
            #         __t = nlp(p['paragraphs'][j]['text'])
            #         sentences = list(__t.sents)
            #         
            #         for s in sentences :
            #             bodyText.append(str(s))
                    
                    bodyText.append(p['paragraphs'][j]['text']) # paragraph-level
                    sectionInfo.append(sectionTitle)
        
        paper_f = open("./slideImages/paperData.txt", "w")
        
        for b in bodyText:
            paper_f.write(b + "\n")
        
        ###############
        
        paper_s = open("./slideImages/sectionData.txt", "w")
        
        print(bodyText)
        print(sectionInfo)

        for b in sectionInfo:
            paper_s.write(b + "\n")


        paper_f.close()
        paper_s.close()

        os.system("python genJsonStructure.py")
    
        os.system("rm -rf ./slideData/" + str(index))
        os.system("mv slideImages slideData/" + str(index))
    
    if index >= 20 :
        break

_f = open("./slideData/summary.json", "w")

_f.write(json.dumps({
    "presentationCnt": len(valid_presentation_index),
    "valid_presentation_index": valid_presentation_index
}))

_f.close()

os.system("rm -rf ../../public/slideData")
os.system("cp -rp ./slideData ../../public")

