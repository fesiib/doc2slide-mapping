import json
import numpy
import sklearn
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

timestamp = open("slideImages/frameTimestamp.txt", "r")
script = open("slideImages/scriptData.txt", "r")
paper = open("slideImages/paperData.txt", "r")
section = open("slideImages/sectionData.txt", "r")

timestampData = []
scriptData = []

def readFile(filename) :
    retValue = []
    f = open(filename, "r")

    while True :
        line = f.readline()

        if not line :
            break
    
        retValue.append(line.strip())
    
    return retValue

paperData = readFile("slideImages/paperData.txt")
sectionData = readFile("slideImages/sectionData.txt")
scriptData = readFile("slideImages/scriptData.txt")

print(len(paperData))
print(len(sectionData))

while True :
    line = timestamp.readline()
    if not line :
        break

    timestampData.append([float(line.split('\t')[0]), float(line.split('\t')[1])])

result = {}

result['title'] = "tempTitle"
result['slideCnt'] = len(timestampData)
result['slideInfo']= []

ocrResult = [];

for i in range(len(timestampData)) :
    ocrFile = open("slideImages/ocr/" + str(i) + ".jpg.txt", "r")

    ocrResult.append('');

    while True :
        line = ocrFile.readline()

        if not line :
            break

        res = line.split('\t')[-1].strip()

        if len(res) > 0 :
            ocrResult[-1] = ocrResult[-1] + ' ' + res

print(ocrResult)

interval = 3

__scriptData = []

for j in range(len(scriptData)) :
    __scriptData.append(' '.join(scriptData[max(j-interval, 0):min(j+interval, len(scriptData))]))


paper_embeddings = model.encode(paperData)
script_embeddings = model.encode(__scriptData)






threshold = 3

post_script = []

similarity = sklearn.metrics.pairwise.cosine_similarity(script_embeddings, paper_embeddings)
__sim = []
__sim_t = []

trans = numpy.transpose(similarity)

for i in range(len(similarity)) :
    top_k = numpy.argsort(similarity[i])[-threshold:]
    prob = similarity[i][top_k[0]]

    __sim.append([val if val >= prob else 0 for idx, val in enumerate(similarity[i])])

for i in range(len(trans)) :
    top_k = numpy.argsort(trans[i])[-threshold:]
    prob = trans[i][top_k[0]]

    __sim_t.append([val if val >= prob else 0 for idx, val in enumerate(trans[i])])

__sim_t = numpy.transpose(__sim_t)

overall = []

for i in range(len(similarity)) :
# overall.append([ min(__sim[i][j], __sim_t[i][j]) for j in range(len(similarity[i]))])
    overall.append([ __sim[i][j] for j in range(len(similarity[i]))]) # less strict version

print(overall)
print(len(overall), len(overall[0]))

# y-axis : slides, x-axis : paper

topSections = []

for i in range(len(overall)) :
    args = numpy.argsort(overall[i])[-threshold:]
    values = sorted(overall[i])[-threshold:]

    v = []

    for j in [2, 1, 0] :
        if values[j] == 0 :
            v.append("NO_SECTION_FOUND")
        else :
            v.append(sectionData[args[j]])

    print(i)
    print(v)
    topSections.append(v)

Table = [ [ 0 for j in range(len(__scriptData))] for i in range(len(__scriptData)) ]

def getSegment(topSections, start, end) :
    if end - start + 1 <= 4 :
        return ('', -99)

    myList = []

    for j in range(start, end+1) :
        myList.append(topSections[j][0])
        myList.append(topSections[j][1])
        myList.append(topSections[j][2])

    myList = list(set(myList))
    value = [ 0 for i in range(len(myList)) ]

    result_section = ''
    result_value = -99

    for i in range(len(myList)) :
        temp = 0
        if myList[i] == "NO_SECTION_FOUND" :
            continue

        for j in range(start, end+1) :
            if topSections[j][0] == myList[i] :
                temp = temp + 3
            if topSections[j][1] == myList[i] :
                temp = temp + 2
            if topSections[j][2] == myList[i] :
                temp = temp + 1

        if result_value < temp :
            result_value = temp
            result_section = myList[i]

    return (result_section, result_value)

for i in range(len(__scriptData)) :
    segResult = getSegment(topSections, 0, i)

    Table[0][i] = (0, segResult[0], segResult[1])

for i in range(1, len(__scriptData)) :
    Table[i][i] = (i, topSections[i][0], 3 + Table[i-1][i-1][2])

    for j in range(i+1, len(__scriptData)) :
        Table[i][j] = (-1, -1, -99)

        for k in range(i-1, j) :
            cost = getSegment(topSections, k+1, j)

            if Table[i][j][2] < Table[i-1][k][2] + cost[1] :
                Table[i][j] = (k, cost[0], Table[i-1][k][2] + cost[1])

myMaxValue = -99
myMaxIndex = -1

weight = []

for i in range(len(__scriptData)) :
    weight.append(Table[i][len(__scriptData)-1][2])

for i in range(len(Table)) :
    if myMaxValue < Table[i][len(__scriptData)-1][2] :
        myMaxValue = Table[i][len(__scriptData)-1][2]
        myMaxIndex = i

print(myMaxIndex, myMaxValue)

finalResult = [ '' for i in range(len(__scriptData)) ]

cur = myMaxIndex
curSlide = len(__scriptData)-1

while True :
    start = Table[cur][curSlide][0]
    curSection = Table[cur][curSlide][1]

    for i in range(start, curSlide+1) :
        finalResult[i] = curSection

    if start <= 0 :
        break

    curSlide = Table[cur][curSlide][0] - 1
    cur = cur - 1

    if cur < 0 :
        print("WHAT???? ERROR ERROR ERROR ERROR")
        break


outline = []

outline.append({
    'section': finalResult[0],
    'startSlideIndex': 0,
    'endSlideIndex': 0
    })

for i in range(1, len(finalResult)) :
    if outline[-1]['section'] != finalResult[i] :
        outline.append({
            'section': finalResult[i],
            'startSlideIndex': i,
            'endSlideIndex': i
        })
    else :
        outline[-1]['endSlideIndex'] = i

print(outline)

for i in range(len(timestampData)) :
    result['slideInfo'].append({
        "index": i,
        "startTime": timestampData[i][0],
        "endTime": timestampData[i][1],
        "script": scriptData[i],
        "ocrResult": ocrResult[i],
    })

result['outline'] = outline

jsonFile = open("slideImages/result.json", "w")
jsonFile.write(json.dumps(result))



