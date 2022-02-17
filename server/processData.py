import json
import os
import re
import numpy
import sklearn
import nltk
from sentence_transformers import SentenceTransformer

#nltk.download('punkt')

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

def getOutlineHyungyu(sectionData, topSections, script_sentence_range):
    uniqueSections = []
    for section in sectionData:
        if section in SKIPPED_SECTIONS or section in uniqueSections:
            continue
        uniqueSections.append(section)

    INF = (len(script_sentence_range) + 1) * 100
    n = len(uniqueSections)

    Table = [ [ (-INF, n, -1) for j in range(len(script_sentence_range))] for i in range(len(script_sentence_range)) ]

    def getSegment(start, end):
        if end - start < 2:
            return (-INF, n)

        scores = [0 for i in range(n)]
        for i in range(start, end):
            innerScores = [-INF for i in range(n)]
            for topSection in topSections[i]:
                pos = uniqueSections.index(topSection[0])
                innerScores[pos] = max(innerScores[pos], topSection[2])
            for j in range(n):
                if innerScores[j] > 0:
                    scores[j] += innerScores[j]
        
        result_section = -1
        for i in range(n):
            if result_section == -1 or scores[result_section] < scores[i]:
                result_section = i

        return (scores[result_section], result_section)

    for i in range(len(script_sentence_range)) :
        segResult = getSegment(0, i + 1)
        Table[0][i] = (segResult[0], segResult[1], 0)

    for i in range(1, len(script_sentence_range)):
        segResult = getSegment(i, i + 1)
        Table[i][i] = (Table[i-1][i-1][0] + segResult[0], segResult[1], i)

        for j in range(i+1, len(script_sentence_range)) :
            for k in range(i-1, j) :
                cost = getSegment(k+1, j+1)
                if Table[i][j][0] < Table[i-1][k][0] + cost[0]:
                    Table[i][j] = (Table[i-1][k][0] + cost[0], cost[1], k + 1)

    weight = []
    for i in range(len(script_sentence_range)) :
        weight.append(Table[i][len(script_sentence_range) - 1][0])

    myMaxValue = -INF
    optSegs = -1

    for i in range(len(Table)) :
        if myMaxValue < Table[i][len(script_sentence_range) - 1][0]:
            myMaxValue = Table[i][len(script_sentence_range) - 1][0]
            optSegs = i

    finalResult = [ 0 for i in range(len(script_sentence_range)) ]

    curSlide = len(script_sentence_range) - 1
    print(myMaxValue, optSegs)

    while optSegs > 0:
        start = Table[optSegs][curSlide][2]
        curSection = Table[optSegs][curSlide][1]

        for i in range(start, curSlide + 1) :
            finalResult[i] = curSection
        
        curSlide = start - 1
        optSegs = optSegs - 1

        if curSlide < 0 :
            print("WHAT???? ERROR ERROR ERROR ERROR")
            break

    outline = []

    outline.append({
        'section': uniqueSections[finalResult[0]],
        'startSlideIndex': 0,
        'endSlideIndex': 0
    })

    for i in range(1, len(finalResult)) :
        if outline[-1]['section'] != uniqueSections[finalResult[i]]:
            outline.append({
                'section': uniqueSections[finalResult[i]],
                'startSlideIndex': i,
                'endSlideIndex': i
            })
        else :
            outline[-1]['endSlideIndex'] = i
    return outline, weight

def getOutlineMaskDP(sectionData, topSections, script_sentence_range):
    uniqueSections = []
    for section in sectionData:
        if section in SKIPPED_SECTIONS or section in uniqueSections:
            continue
        uniqueSections.append(section)

    n = len(uniqueSections)
    m = len(script_sentence_range)
    INF = (m + 1) * 100

    dp = [[(-INF, n, -1) for j in range(m + 1)] for i in range(1 << n)]
    dp[0][1] = (0, n)

    for i in range(m):
        print(i)
        scores = [-INF for k in range(n)]
        for j in range(i + 1, m + 1):
            for topSection in topSections[j - 1]:
                pos = uniqueSections.index(topSection[0])
                scores[pos] = max(scores[pos], topSection[2])

            for mask in range(0, (1 << n)):
                if dp[mask][i][0] < 0:
                    continue
                for k in range (n):
                    if mask & (1 << k) > 0:
                        continue
                    nmask = mask | (1 << k)
                    if (dp[nmask][j][0] < dp[mask][i][0] + scores[k]):
                        dp[nmask][j] = (scores[k], k, i)

    recoverMask = 0
    recoverSlideId = m

    for mask in range(1 << n):
        if dp[mask][recoverSlideId][0] > dp[recoverMask][recoverSlideId][0] \
            or (bin(mask).count('1') < bin(recoverMask).count('1') and dp[mask][recoverSlideId][0] == dp[recoverMask][recoverSlideId][0]
        ):
            recoverMask = mask

    outline = []
    while recoverSlideId > 1:
        print(recoverMask, recoverSlideId, dp[recoverMask][recoverSlideId])
        sectionId = dp[recoverMask][recoverSlideId][1]
        nextRecoverMask = recoverMask ^ (1 << sectionId)
        nextRecoverSlideId = dp[recoverMask][recoverSlideId][2]
        outline.append({
            "section": uniqueSections[sectionId],
            "startSlideIndex": nextRecoverSlideId,
            "endSlideIndex": recoverSlideId - 1,
        })
        recoverMask = nextRecoverMask
        recoverSlideId = nextRecoverSlideId
    
    return outline[::-1]

def getOutlineSimple(topSections):
    outline = []

    for i in range(1, len(topSections)):
        scores = {
            "NO_SECTION": 0
        }
        for j in range(0, len(topSections[i])):
            if topSections[i][j][0] not in scores:
                scores[topSections[i][j][0]] = 0    
            scores[topSections[i][j][0]] = max(scores[topSections[i][j][0]], topSections[i][j][2])
        section = "NO_SECTION"
        for (k, v) in scores.items():
            if v > scores[section]:
                section = k
        outline.append({
            "section": section,
            "startSlideIndex": i,
            "endSlideIndex": i,
        })
    return outline


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
    
    for i in range(len(timestampData)) :
        result['slideInfo'].append({
            "index": i,
            "startTime": timestampData[i][0],
            "endTime": timestampData[i][1],
            "script": scriptData[i],
            "ocrResult": ocrResult[i],
        })

    # Statement-level for Scripts
    __scriptData = []
    script_sentence_range = []
    for i, (script, ocr) in enumerate(zip(scriptData, ocrResult)):
        if (len(__scriptData) > 300):
            break
        sentences = nltk.sent_tokenize(script)
        #sentences.extend(nltk.sent_tokenize(ocr))
        script_sentence_range.append(len(sentences))
        __scriptData.extend(sentences)

    __paperData = []
    paper_sentence_id = []
    for i, paragraph in enumerate(paperData):
        if (sectionData[i].strip() in SKIPPED_SECTIONS or len(nltk.word_tokenize(paragraph)) < MIN_PARAGRAPH_LENGTH):
            continue
        if (len(__paperData) > 300):
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
        sections = []
        for sectionId in sectionIds:
            if sectionData[sectionId] in SKIPPED_SECTIONS:
                continue
            sections.append((sectionData[sectionId], int(sectionId), sectionScores[sectionId]))

        topSections.append(sections)
        script_sentence_start += script_sentence_range[i]
    
    result['topSections'] = topSections

    
    outline, weight = getOutlineHyungyu(sectionData, topSections, script_sentence_range)

    result['outline'] = outline
    result['weight'] = weight

    result["similarityTable"] = numpy.float64(overall).tolist()
    result["scriptSentences"] = __scriptData
    result["paperSentences"] = __paperData

    jsonFile = open(os.path.join(paper_path, "result.json"), "w")
    jsonFile.write(json.dumps(result))
    return result

if __name__ == "__main__":
    output = process('./slideMeta/slideData/0', './slideMeta/slideData/0')
    #print(output)