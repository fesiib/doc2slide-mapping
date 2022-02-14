import pandas as pd
import os

flag = 1 # 1 : already created, 0: newly create

dataFile = pd.read_csv("../data.csv")
cnt = 0

os.system("rm -rf ./slideData/slideImages")

for index, row in dataFile.iterrows() :
    title = row['title']
    paper = row['paper_file']
    video = row['video_file']
    subtitle = row['subtitle_file']
    videoURL = row['video_url']

    print(index, title, paper, video, subtitle, videoURL)
    print('')

    if flag == 0 :
        os.system("cp ../" + video + " ./video.mp4")
        os.system("cp ../" + subtitle + " ./subtitle.srt")
    
        os.system("rm -rf slideImages")
    
        os.system("sh genSlides.sh")
        os.system("sh genOCR.sh")
        os.system("python getSubtitle.py")
    
        os.system("cp ../paperParsed/" + str(index+1) + ".txt ./slideImages/paperData.txt")
        os.system("cp ../sectionParsed/" + str(index+1) + ".txt ./slideImages/sectionData.txt")
    
        os.system("python genJsonStructure.py")
    
        os.system("mv slideImages slideData")
    
        os.system("rm -rf ./slideData/" + str(index))
    
        os.system("mv slideData/slideImages ./slideData/" + str(index))
    else :
        os.system("rm -rf slideImages")

        os.system("cp -rp ./slideData/" + str(index) + " ./slideImages")
        os.system("python genJsonStructure.py")
    
        os.system("mv slideImages slideData")
    
        os.system("rm -rf ./slideData/" + str(index))
    
        os.system("mv slideData/slideImages ./slideData/" + str(index))

    cnt = cnt + 1

    if index >= 5 :
        break

cmd = 'echo \'{"presentationCnt": ' + str(cnt) + '}\' > slideData/summary.json'
os.system(cmd)
