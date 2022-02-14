#!/bin/bash
index=0
INPUT=../data.csv
OLDIFS=$IFS
IFS=','

[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

rm -rf slideData
mkdir slideData

while IFS=',' read index title paperfile videofile subtitleFile videoUrl dataImported
do
    echo "Name : $title"
    echo "paper: $paperfile"
    echo "video: $videofile"
    echo "subtitle: $subtitleFile"

    subtitleFile=$(echo ${subtitleFile//[$'\t\r\n']})

    echo $subtitleFile
    echo $index

    if [ $index -eq 7 ]
    then
#       cp papers/$paperfile ../../pdffigures2/paper.pdf

#       cd ../../pdffigures2
#       sbt "runMain org.allenai.pdffigures2.FigureExtractorBatchCli paper.pdf -g myPrefix"

#       cp myPrefixpaper.json ../browsingMapping/server/paperData/$index.json

#       cd ../browsingMapping/server

#         mkdir ./frame/$index
# 
#         echo python computeSimilarity.py "$subtitleFile" "./paperData/$index.json"
# 
#         python computeSimilarity.py "$videofile" "$subtitleFile" "./paperData/$index.json" "$index"

        echo "cp ../$videofile ./video.mp4"
        cp ../$videofile ./video.mp4

        echo "cp ../$subtitleFile ./subtitle.srt"
        cp ../$subtitleFile ./subtitle.srt

        rm -rf slideImages

        sh genSlides.sh
        sh genOCR.sh
        python getSubtitle.py
        python genJsonStructure.py

        echo "mv slideImages slideData"
        mv slideImages slideData

        echo "mv slideData/slideImages $index"
        mv slideData/slideImages ./slideData/$index

#        if [ $index -gt 2 ]
#        then
#            break
#        fi
    fi

    index=$((index+1))

    echo '{"presentationCnt": '{{$index+1}}'}' > slideData/summary.json

done < $INPUT
IFS=$OLDIFS

