import json
import os
import numpy
import sklearn
import nltk
from sentence_transformers import SentenceTransformer

nltk.download('punkt')

model = SentenceTransformer('all-MiniLM-L6-v2')

SKIPPED_SECTIONS = [
    "CCS CONCEPTS",
    "ACM Reference Format:",
    "REFERENCES",
]
MIN_PARAGRAPH_LENGTH = 10
    
def readFile(filename) :
    retValue = []
    f = open(filename, "r")

    while True :
        line = f.readline()

        if not line :
            break
    
        retValue.append(line.strip())
    
    return retValue

def process(paper_path, script_path):
    timestamp = open(os.path.join(script_path, "frameTimestamp.txt"), "r")

    timestampData = []
    scriptData = []

    paperData = readFile(os.path.join(paper_path, "paperData.txt"))
    sectionData = readFile(os.path.join(paper_path, "sectionData.txt"))
    scriptData = readFile(os.path.join(script_path, "scriptData.txt"))

    while True :
        line = timestamp.readline()
        if not line :
            break
        timestampData.append([float(line.split('\t')[0]), float(line.split('\t')[1])])

    result = {}

    result['title'] = "tempTitle"
    result['slideCnt'] = len(timestampData)
    result['slideInfo']= []

    ocrResult = []

    for i in range(len(timestampData)) :
        ocrFile = open(os.path.join(script_path, "ocr", str(i) + ".jpg.txt"), "r")

        ocrResult.append('')

        while True :
            line = ocrFile.readline()
            if not line :
                break
            res = line.split('\t')[-1].strip()
            if len(res) > 0 :
                ocrResult[-1] = ocrResult[-1] + '. ' + res


    # Concatenating Nearby Scripts
    # interval = 4
    # __scriptData = []
    # for j in range(len(scriptData)) :
    #     __scriptData.append(' '.join(scriptData[max(j-interval, 0):min(j+interval, len(scriptData))]))

    # Statement-level for Scripts
    __scriptData = []
    script_sentence_range = []
    for script, ocr in zip(scriptData, ocrResult):
        if (len(__scriptData) > 150):
            break
        sentences = nltk.sent_tokenize(script)
        #sentences.extend(nltk.sent_tokenize(ocr))
        script_sentence_range.append(len(sentences))
        __scriptData.extend(sentences)

    __paperData = []
    paper_sentence_id = []
    for i, paragraph in enumerate(paperData):
        # if (sectionData[i].startswith("5 STUDY 2:") is False and sectionData[i].startswith("Sources") is False):
        #     continue

        if (sectionData[i].strip() in SKIPPED_SECTIONS or len(nltk.word_tokenize(paragraph)) < MIN_PARAGRAPH_LENGTH):
            continue
        if (len(__paperData) > 500):
            break
        sentences = nltk.sent_tokenize(paragraph)
        for j in range(len(__paperData), len(sentences) + len(__paperData)):
            paper_sentence_id.append(i)
        __paperData.extend(sentences)

    print("Sentences# {} Scripts# {}".format(len(__scriptData), len(scriptData)))
    print("Sentences# {} Paragraphs# {}".format(len(__paperData), len(paperData)))
    

    paper_embeddings = model.encode(__paperData)
    script_embeddings = model.encode(__scriptData)

    threshold = 10
    val_threshold = 0.4
    
    similarity = sklearn.metrics.pairwise.cosine_similarity(paper_embeddings, script_embeddings)
    ###similarity = (similarity - numpy.min(similarity) / (numpy.max(similarity) - numpy.min(similarity)))
    trans = numpy.transpose(similarity)
    
    __sim = []
    __sim_t = []
    
    for i in range(len(similarity)) :
        top_k = numpy.argsort(similarity[i])[-threshold:]
        prob = similarity[i][top_k[0]]
        prob = max(prob, val_threshold)

        __sim.append([val if val >= prob else 0 for idx, val in enumerate(similarity[i])])

    for i in range(len(trans)) :
        top_k = numpy.argsort(trans[i])[-threshold:]
        prob = trans[i][top_k[0]]
        prob = max(prob, val_threshold)

        __sim_t.append([val if val >= prob else 0 for idx, val in enumerate(trans[i])])

    __sim_t = numpy.transpose(__sim_t)

    overall = numpy.zeros((len(__sim), len(__sim[0])))

    for i in range(len(__sim)):
        for j in range(len(__sim[i])):
            overall[i][j] = max(__sim[i][j], __sim_t[i][j])


    # for i in range(len(similarity)) :
    #     # overall.append([ min(__sim[i][j], __sim_t[i][j]) for j in range(len(similarity[i]))])
    #     overall.append([ __sim[i][j] for j in range(len(similarity[i]))]) # less strict version

    print(overall.shape)

    # y-axis : slides, x-axis : paper

    topSections = []

    script_sentence_start = 0

    for i in range(len(script_sentence_range)):
        sectionScores = numpy.zeros(len(sectionData), dtype=numpy.float64)
        for j in range(script_sentence_start, script_sentence_start + script_sentence_range[i]):
            args = numpy.argsort(overall[:, j])[-threshold:]
            for pos in args:
                sectionScores[paper_sentence_id[pos]] += overall[pos][j]
        sectionIds = numpy.argsort(sectionScores)[-threshold:]
        sections = [(sectionData[sectionId], int(sectionId), sectionScores[sectionId]) for sectionId in sectionIds]

        topSections.append(sections)
        script_sentence_start += script_sentence_range[i]
    

    # Table = [ [ 0 for j in range(len(__scriptData))] for i in range(len(__scriptData)) ]

    # def getSegment(topSections, start, end) :
    #     if end - start + 1 <= 4 :
    #         return ('', -99)

    #     myList = []

    #     for j in range(start, end+1) :
    #         myList.append(topSections[j][0])
    #         myList.append(topSections[j][1])
    #         myList.append(topSections[j][2])

    #     myList = list(set(myList))
    #     value = [ 0 for i in range(len(myList)) ]

    #     result_section = ''
    #     result_value = -99

    #     for i in range(len(myList)) :
    #         temp = 0
    #         if myList[i] == "NO_SECTION_FOUND" :
    #             continue

    #         for j in range(start, end+1) :
    #             if topSections[j][0] == myList[i] :
    #                 temp = temp + 3
    #             if topSections[j][1] == myList[i] :
    #                 temp = temp + 2
    #             if topSections[j][2] == myList[i] :
    #                 temp = temp + 1

    #         if result_value < temp :
    #             result_value = temp
    #             result_section = myList[i]

    #     return (result_section, result_value)

    # for i in range(len(__scriptData)) :
    #     segResult = getSegment(topSections, 0, i)

    #     Table[0][i] = (0, segResult[0], segResult[1])

    # for i in range(1, len(__scriptData)) :
    #     Table[i][i] = (i, topSections[i][0], 3 + Table[i-1][i-1][2])

    #     for j in range(i+1, len(__scriptData)) :
    #         Table[i][j] = (-1, -1, -99)

    #         for k in range(i-1, j) :
    #             cost = getSegment(topSections, k+1, j)

    #             if Table[i][j][2] < Table[i-1][k][2] + cost[1] :
    #                 Table[i][j] = (k, cost[0], Table[i-1][k][2] + cost[1])

    # myMaxValue = -99
    # myMaxIndex = -1

    # weight = []

    # for i in range(len(__scriptData)) :
    #     weight.append(Table[i][len(__scriptData)-1][2])

    # for i in range(len(Table)) :
    #     if myMaxValue < Table[i][len(__scriptData)-1][2] :
    #         myMaxValue = Table[i][len(__scriptData)-1][2]
    #         myMaxIndex = i

    # finalResult = [ '' for i in range(len(__scriptData)) ]

    # cur = myMaxIndex
    # curSlide = len(__scriptData)-1

    # while True :
    #     start = Table[cur][curSlide][0]
    #     curSection = Table[cur][curSlide][1]

    #     for i in range(start, curSlide+1) :
    #         finalResult[i] = curSection

    #     if start <= 0 :
    #         break

    #     curSlide = Table[cur][curSlide][0] - 1
    #     cur = cur - 1

    #     if cur < 0 :
    #         print("WHAT???? ERROR ERROR ERROR ERROR")
    #         break


    outline = []

    for i in range(1, len(topSections)):
        scores = {
            "NO_SECTION": 0
        }
        for j in range(0, len(topSections[i])):
            if topSections[i][j][0] not in scores:
                scores[topSections[i][j][0]] = 0    
            scores[topSections[i][j][0]] += topSections[i][j][2]
        section = "NO_SECTION"
        for (k, v) in scores.items():
            if v > scores[section]:
                section = k
        outline.append({
            "section": section,
            "startSlideIndex": i,
            "endSlideIndex": i,
        })

    # outline.append({
    #     'section': finalResult[0],
    #     'startSlideIndex': 0,
    #     'endSlideIndex': 0
    #     })

    # for i in range(1, len(finalResult)) :
    #     if outline[-1]['section'] != finalResult[i] :
    #         outline.append({
    #             'section': finalResult[i],
    #             'startSlideIndex': i,
    #             'endSlideIndex': i
    #         })
    #     else :
    #         outline[-1]['endSlideIndex'] = i

    for i in range(len(timestampData)) :
        result['slideInfo'].append({
            "index": i,
            "startTime": timestampData[i][0],
            "endTime": timestampData[i][1],
            "script": scriptData[i],
            "ocrResult": ocrResult[i],
        })

    result['outline'] = outline
    result['topSections'] = topSections
    #result['weight'] = weight

    result["similarityTable"] = numpy.float64(overall).tolist()
    result["scriptSentences"] = __scriptData
    result["paperSentences"] = __paperData

    jsonFile = open(os.path.join(paper_path, "result.json"), "w")
    jsonFile.write(json.dumps(result))
    return result

if __name__ == "__main__":
    output = process('./slideMeta/slideData/0', './slideMeta/slideData/0')
    #print(output)