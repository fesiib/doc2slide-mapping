import json
import os
import numpy
import sklearn

import spacy

from nltk.tokenize import sent_tokenize, word_tokenize

from sentence_transformers import SentenceTransformer

from string import ascii_lowercase, punctuation, digits

#nltk.download('punkt')

SKIPPED_SECTIONS = [
    "CCS CONCEPTS",
    "KEYWORDS",
    "ACM Reference Format:",
    "REFERENCES",
    "ACKNOWLEDGMENTS"
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

def is_section_skipped(section):
    for skipped_section in SKIPPED_SECTIONS:
        if skipped_section in section:
            return True
    return False

def makeLemma(token):
    return token.lemma_.lower().strip()

def actual_word(word):
    for ch in word:
        if ch not in ascii_lowercase and ch not in digits:
            return False
    return True

def getKeywords(text, nlp):
    STOP_WORDS = spacy.lang.en.stop_words.STOP_WORDS
    tokens = nlp(text)
    tokens = [ makeLemma(word) for word in tokens if word.lemma_ != "-PRON-"]
    tokens = [ word for word in tokens if word not in STOP_WORDS and word not in punctuation]
    tokens = [ word for word in tokens if actual_word(word)]

    return list(set(tokens))

def applyThresholds(array_2d, top_k, val_threshold):
    ret_array = []

    for i in range(len(array_2d)) :
        args = numpy.argsort(array_2d[i])[-top_k:]
        prob = array_2d[i][args[0]]
        prob = max(prob, val_threshold)

        ret_array.append([val if val >= prob else 0 for val in array_2d[i]])
    
    return ret_array

def getSimilarityEmbedding(paperData, scriptData, sectionData, paper_sentence_id, script_sentence_range):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    paper_embeddings = model.encode(paperData)
    script_embeddings = model.encode(scriptData)

    top_k = 20
    val_threshold = 0.0
    
    similarity = sklearn.metrics.pairwise.cosine_similarity(paper_embeddings, script_embeddings)
    trans = numpy.transpose(similarity)
    
    __sim = applyThresholds(similarity, top_k, val_threshold)
    __sim_t = applyThresholds(trans, top_k, val_threshold)

    __sim_t = numpy.transpose(__sim_t)

    overall = numpy.zeros((len(__sim), len(__sim[0])))

    for i in range(len(__sim)):
        for j in range(len(__sim[i])):
            overall[i][j] = max(__sim[i][j], __sim_t[i][j])

    # y-axis : slides, x-axis : paper

    topSections = []

    script_sentence_start = 0

    for i in range(len(script_sentence_range)):
        sectionScores = numpy.zeros(len(sectionData), dtype=numpy.float64)
        for j in range(script_sentence_start, script_sentence_start + script_sentence_range[i]):
            args = numpy.argsort(overall[:, j])[-top_k:]
            for pos in args:
                sectionScores[paper_sentence_id[pos]] += overall[pos][j]
        sectionIds = numpy.argsort(sectionScores)[-top_k:]
        sections = []
        for sectionId in sectionIds:
            if is_section_skipped(sectionData[sectionId]):
                continue
            sections.append((sectionData[sectionId], int(sectionId), sectionScores[sectionId]))

        topSections.append(sections)
        script_sentence_start += script_sentence_range[i]
    
    return overall, topSections


def getSimilarityKeywords(paperData, scriptData, sectionData, paper_sentence_id, script_sentence_range):
    nlp = spacy.load("en_core_web_sm")
    similarity = numpy.zeros((len(paperData), len(scriptData)))

    paperKeywords = []
    scriptKeywords = []

    top_k = 20
    val_threshold = 4
    
    for paper_sentence in paperData:
        paperKeywords.append(getKeywords(paper_sentence, nlp))

    
    for script_sentence in scriptData:
        scriptKeywords.append(getKeywords(script_sentence, nlp))

    for i in range(len(paperKeywords)):
        for j in range(len(scriptKeywords)):
            intersection = 0
            union = 0
            for keyword in paperKeywords[i]:
                if keyword in scriptKeywords[j]:
                    intersection += 1
            union = (len(paperKeywords[i]) + len(scriptKeywords[j])) - intersection
            ## intersection over union
            similarity[i][j] = 0
            if union > 0:
                similarity[i][j] = intersection / union

    similarity_t = numpy.transpose(similarity)

    #similarity = applyThresholds(similarity, top_k, val_threshold)
    #similarity_t = applyThresholds(similarity_t, top_k, val_threshold)

    similarity_t = numpy.transpose(similarity_t)

    overall = numpy.zeros((len(similarity), len(similarity[0])))

    for i in range(len(similarity)):
        for j in range(len(similarity[i])):
            overall[i][j] = max(similarity[i][j], similarity_t[i][j])

    topSections = []

    script_sentence_start = 0

    for i in range(len(script_sentence_range)):
        sectionScores = numpy.zeros(len(sectionData), dtype=numpy.float64)
        for j in range(script_sentence_start, script_sentence_start + script_sentence_range[i]):
            args = numpy.argsort(overall[:, j]) [-top_k:]
            for pos in args:
                sectionScores[paper_sentence_id[pos]] += overall[pos][j]
        sectionIds = numpy.argsort(sectionScores) [-top_k:]
        sections = []
        for sectionId in sectionIds:
            if is_section_skipped(sectionData[sectionId]):
                continue
            sections.append((sectionData[sectionId], int(sectionId), sectionScores[sectionId]))

        topSections.append(sections)
        script_sentence_start += script_sentence_range[i]
    
    return overall, topSections, paperKeywords, scriptKeywords

def getOutlineHyungyu(sectionData, topSections, script_sentence_range):
    uniqueSections = []
    for section in sectionData:
        if is_section_skipped(section) or section in uniqueSections:
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

    Table[0][0] = (0, n, 0)

    for i in range(1, len(script_sentence_range)):
        segResult = getSegment(i, i + 1)

        Table[i][i] = (max(Table[i-1][i-1][0] + segResult[0], Table[i][i][0]), segResult[1], i)

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
        'section': "NO_SECTION",
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
        if is_section_skipped(section) or section in uniqueSections:
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

def fixSectionTitles(section_titles):
    ret_titles = []

    title_num = 0

    last_section = None

    def is_main_section(title):
        if title[0] in digits or title.isupper() is True:
            return True
        return False


    for title in section_titles:
        if is_main_section(title) or last_section is None:
            ret_titles.append(title)
            last_section = title
        else:
            ret_titles.append(last_section) 
    return ret_titles


def process(paper_path, script_path):
    timestamp = open(os.path.join(script_path, "frameTimestamp.txt"), "r")

    timestampData = []
    scriptData = []

    paperData = readFile(os.path.join(paper_path, "paperData.txt"))
    sectionData = readFile(os.path.join(paper_path, "sectionData.txt"))
    scriptData = readFile(os.path.join(script_path, "scriptData.txt"))

    sectionData = fixSectionTitles(sectionData)

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
        # if (len(__scriptData) > 10):
        #     break
        sentences = sent_tokenize(script)
        sentences.append(ocr)
        script_sentence_range.append(len(sentences))
        __scriptData.extend(sentences)

    __paperData = []
    paper_sentence_id = []
    for i, paragraph in enumerate(paperData):
        if (is_section_skipped(sectionData[i]) or len(word_tokenize(paragraph)) < MIN_PARAGRAPH_LENGTH):
            continue
        # if (len(__paperData) > 10):
        #     break
        sentences = sent_tokenize(paragraph)
        for j in range(len(__paperData), len(sentences) + len(__paperData)):
            paper_sentence_id.append(i)
        __paperData.extend(sentences)

    print("Sentences# {} Scripts# {}".format(len(__scriptData), len(scriptData)))
    print("Sentences# {} Paragraphs# {}".format(len(__paperData), len(paperData)))

    #overall, topSections = getSimilarityEmbedding(__paperData, __scriptData, sectionData, paper_sentence_id, script_sentence_range)
    overall, topSections, paperKeywords, scriptKeywords = getSimilarityKeywords(__paperData, __scriptData, sectionData, paper_sentence_id, script_sentence_range)

    outline, weight = getOutlineHyungyu(sectionData, topSections, script_sentence_range)

    overall = overall / numpy.amax(overall)

    result['topSections'] = topSections

    result['outline'] = outline
    result['weight'] = weight

    result["similarityTable"] = numpy.float64(overall).tolist()
    result["scriptSentences"] = scriptKeywords
    result["paperSentences"] = paperKeywords

    jsonFile = open(os.path.join(paper_path, "result.json"), "w")
    jsonFile.write(json.dumps(result))
    return result

if __name__ == "__main__":
    output = process('./slideMeta/slideData/0', './slideMeta/slideData/0')
    print(output["outline"])