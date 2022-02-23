import json
import os
import re
import numpy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity

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

class Vectorizer(object):
    def __init__(self, method='tf-idf'):
        self.method = method
        self.vectorizer = None

        if method == 'tf-idf':
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 4))
        elif method == 'embedding':
            self.vectorizer = SentenceTransformer('all-MiniLM-L6-v2')
    
    def fit_transform(self, data):
        if self.method == 'tf-idf':
            return self.vectorizer.fit_transform(data)
        return self.vectorizer.encode(data)
    
    def transform(self, data):
        if self.method == 'tf-idf':
            return self.vectorizer.transform(data)
        elif self.method == 'embedding':
            return self.vectorizer.encode(data)
        return None

    
def read_txt(path) :
    lines = []
    with open(path, "r") as f:
        while True :
            line = f.readline()
            if not line :
                break
            lines.append(line.strip())
    return lines


def read_json(path):
    obj = {}
    with open(path, 'r') as f:
        encoded = f.read()
        obj = json.loads(encoded)
    return obj     


def is_section_skipped(section):
    for skipped_section in SKIPPED_SECTIONS:
        if skipped_section in section:
            return True
    return False

def make_lemma(token):
    return token.lemma_.lower().strip()

def actual_word(word):
    for ch in word:
        if ch not in ascii_lowercase and ch not in digits:
            return False
    return True


def preprocess_text(t):
    t = re.sub(r'[^\w\s]', '', t)
    return t.lower().strip()

def get_keywords(text, nlp):
    STOP_WORDS = spacy.lang.en.stop_words.STOP_WORDS
    text = preprocess_text(text)
    tokens = nlp(text)
    tokens = [ make_lemma(word) for word in tokens if word.lemma_ != "-PRON-"]
    tokens = [ word for word in tokens if word not in STOP_WORDS and word not in punctuation]
    #tokens = [ word for word in tokens if actual_word(word)]

    return list(tokens)

def get_sentences(t) :
    sentences = sent_tokenize(t)
    return sentences

def apply_thresholds_2darray(array_2d, top_k, val_threshold):
    ret_array = []

    for i in range(len(array_2d)) :
        args = numpy.argsort(array_2d[i])[-top_k:]
        prob = array_2d[i][args[0]]
        prob = max(prob, val_threshold)

        ret_array.append([val if val >= prob else 0 for val in array_2d[i]])
    
    return ret_array

def get_top_sections(overall, section_data, script_sentence_range, paper_sentence_id, apply_thresholding, top_k):
    overall = numpy.array(overall)

    top_paragraphs = []

    script_sentence_start = 0

    for i in range(len(script_sentence_range)):
        section_scores = numpy.zeros(len(section_data), dtype=numpy.float64)
        for j in range(script_sentence_start, script_sentence_start + script_sentence_range[i]):
            args = numpy.argsort(overall[:, j])
            if apply_thresholding is True:
                args = args[-top_k:]
            for pos in args:
                section_scores[paper_sentence_id[pos]] += overall[pos][j]
        section_ids = numpy.argsort(section_scores)
        if apply_thresholding is True:
            section_ids = section_ids[-top_k:]
        sections = []
        for section_id in section_ids:
            sections.append((section_data[section_id], int(section_id), section_scores[section_id]))

        top_paragraphs.append(sections)
        script_sentence_start += script_sentence_range[i]
    
    top_sections = []

    for paragraphs in top_paragraphs:
        map_sections = {}
        for top_paragraph in paragraphs:
            if top_paragraph[0] not in map_sections:
                map_sections[top_paragraph[0]] = top_paragraph[2]
            else:
                # Sum -> biased, max -> might not be the best
                map_sections[top_paragraph[0]] = max(map_sections[top_paragraph[0]], top_paragraph[2])
        sections = []
        for (k, v) in map_sections.items():
            sections.append([k, v])
        top_sections.append(sections)
    return top_sections

def get_similarity_classifier(paper_data, script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding):
    top_k = 5
    val_threshold = 0.1

    label_dict = sorted(list(set(section_data)))
    label_categories = [ label_dict.index(section_data[sentence_id]) for sentence_id in paper_sentence_id ]

    model = RandomForestClassifier()
    
    vectorizer = Vectorizer(method = 'tf-idf')
    X = vectorizer.fit_transform(list(map(preprocess_text, paper_data)))
    print(X.shape)

    Y = numpy.array(*[label_categories])
    print(Y.shape)

    model.fit(X, Y)

    def get_all_probs(t) :
        pre = ' '.join(map(preprocess_text, get_sentences(t)))
        X2 = vectorizer.transform([pre])
        return model.predict_proba(X2)[0]

    paper_data_by_section = [[] for i in range(len(label_dict))]
    for i, sentence in enumerate(paper_data):
        paper_data_by_section[label_categories[i]].append(" " + sentence)

    overall = []
    for script in script_data:
        #tokens = word_tokenize(scriptData[i])
        overall.append(get_all_probs(script))

    if apply_thresholding is True:
        overall_t = numpy.transpose(overall)
        
        overall = apply_thresholds_2darray(overall, top_k, val_threshold)
        overall_t = apply_thresholds_2darray(overall_t, top_k, val_threshold)
        
        overall_t = numpy.transpose(overall_t)

        for i in range(len(overall)):
            for j in range(len(overall[i])):
                overall[i][j] = max(overall[i][j], overall_t[i][j])

    top_sections = []
    script_sentence_start = 0

    for i in range(len(script_sentence_range)):
        section_ids = numpy.argsort(overall[i])
        if apply_thresholding is True:
            section_ids = section_ids[-top_k:]
        sections = []
        for section_id in section_ids:
            sections.append((label_dict[section_id], overall[i][section_id]))
        top_sections.append(sections)
        script_sentence_start += script_sentence_range[i]

    return overall, top_sections, paper_data_by_section

def get_similarity_embeddings(paper_data, script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding):
    vectorizer = Vectorizer(method='embedding')

    paper_embeddings = vectorizer.transform(paper_data)
    script_embeddings = vectorizer.transform(script_data)

    top_k = 10
    val_threshold = 0.6
    
    overall = cosine_similarity(paper_embeddings, script_embeddings)

    if apply_thresholding is True:
        overall_t = numpy.transpose(overall)

        overall = apply_thresholds_2darray(overall, top_k, val_threshold)
        overall_t = apply_thresholds_2darray(overall_t, top_k, val_threshold)

        overall_t = numpy.transpose(overall_t)

        for i in range(len(overall)):
            for j in range(len(overall[i])):
                overall[i][j] = max(overall[i][j], overall_t[i][j])

    top_sections = get_top_sections(overall, section_data, script_sentence_range, paper_sentence_id, apply_thresholding, top_k)
    
    return overall, top_sections


def get_similarity_keywords(paper_data, script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding):
    nlp = spacy.load("en_core_web_sm")
    vectorizer = TfidfVectorizer(ngram_range=(1, 1), min_df=0, max_df=1.0)

    overall = numpy.zeros((len(paper_data), len(script_data)))

    paper_keywords = []
    script_keywords = []

    top_k = 10
    val_threshold = 0.2
    
    for paper_sentence in paper_data:
        paper_keywords.append(get_keywords(paper_sentence, nlp))

    for script_sentence in script_data:
        script_keywords.append(get_keywords(script_sentence, nlp))

    LOL = vectorizer.fit_transform(map(' '.join, paper_keywords))
    vectorizer_features = vectorizer.get_feature_names_out().tolist()

    print(LOL.shape, vectorizer_features)

    # for i in range(len(paper_keywords)):
    #     for j in range(len(script_keywords)):
    #         intersection = 0
    #         union = 0
    #         for keyword in paper_keywords[i]:
    #             if keyword in script_keywords[j]:
    #                 intersection += 1
    #         union = (len(paper_keywords[i]) + len(script_keywords[j])) - intersection
    #         ## intersection over union
    #         overall[i][j] = 0
    #         if union > 0:
    #             overall[i][j] = intersection / union

    for j in range(len(script_keywords)):
        X = vectorizer.transform([' '.join(script_keywords[j])])
        unique_keywords = list(set(script_keywords[j]))
        score_for_each = []
        for word in unique_keywords:
            try:
                score_for_each.append(1.0 - X[0, vectorizer_features.index(word)])
            except:
                score_for_each.append(0.0)

        # if 'intelligent' in unique_keywords and 'response' in unique_keywords:
        #     print([(word, score) for (word, score) in zip(unique_keywords, score_for_each)])
        for i in range(len(paper_keywords)):
            for k, word in enumerate(unique_keywords):
                if word in paper_keywords[i]:
                    overall[i][j] += score_for_each[k]
            

    if apply_thresholding is True:
        overall_t = numpy.transpose(overall)

        overall = apply_thresholds_2darray(overall, top_k, val_threshold)
        overall_t = apply_thresholds_2darray(overall_t, top_k, val_threshold)

        overall_t = numpy.transpose(overall_t)

        for i in range(len(overall)):
            for j in range(len(overall[i])):
                overall[i][j] = max(overall[i][j], overall_t[i][j])

    

    top_sections = get_top_sections(overall, section_data, script_sentence_range, paper_sentence_id, apply_thresholding, top_k)
    
    return overall, top_sections, paper_keywords, script_keywords

def get_outline_dp(section_data, top_sections, script_sentence_range):
    label_dict = sorted(list(set(section_data)))
    
    INF = (len(script_sentence_range) + 1) * 100
    n = len(label_dict)

    Table = [ [ (-INF, n, -1) for j in range(len(script_sentence_range))] for i in range(len(script_sentence_range)) ]

    def getSegment(start, end):
        if end - start < 2:
            return (-INF, n)

        scores = [0 for i in range(n)]
        for i in range(start, end):
            for top_section in top_sections[i]:
                pos = label_dict.index(top_section[0])
                scores[pos] += top_section[1]
        result_section = -1
        for i in range(n):
            if result_section == -1 or scores[result_section] < scores[i]:
                result_section = i

        return (scores[result_section], result_section)

    Table[0][0] = (0, n, 0)

    for i in range(1, len(script_sentence_range)):
        segment_result = getSegment(i, i + 1)

        Table[i][i] = (max(Table[i-1][i-1][0] + segment_result[0], Table[i][i][0]), segment_result[1], i)

        for j in range(i+1, len(script_sentence_range)) :
            for k in range(i-1, j) :
                cost = getSegment(k+1, j+1)
                if Table[i][j][0] < Table[i-1][k][0] + cost[0]:
                    Table[i][j] = (Table[i-1][k][0] + cost[0], cost[1], k + 1)

    weights = []
    for i in range(len(script_sentence_range)) :
        weights.append(Table[i][len(script_sentence_range) - 1][0])

    max_value = -INF
    optimal_segments = -1

    for i in range(len(Table)) :
        if max_value < Table[i][len(script_sentence_range) - 1][0]:
            max_value = Table[i][len(script_sentence_range) - 1][0]
            optimal_segments = i

    final_result = [ 0 for i in range(len(script_sentence_range)) ]

    cur_slide = len(script_sentence_range) - 1
    print(max_value, optimal_segments)

    while optimal_segments > 0:
        start = Table[optimal_segments][cur_slide][2]
        cur_section = Table[optimal_segments][cur_slide][1]

        for i in range(start, cur_slide + 1) :
            final_result[i] = cur_section
        
        cur_slide = start - 1
        optimal_segments = optimal_segments - 1

        if cur_slide < 0 :
            print("WHAT???? ERROR ERROR ERROR ERROR")
            break

    outline = []

    outline.append({
        'sectionTitle': "NO_SECTION",
        'startSlideIndex': 0,
        'endSlideIndex': 0
    })

    for i in range(1, len(final_result)) :
        if outline[-1]['sectionTitle'] != label_dict[final_result[i]]:
            outline.append({
                'sectionTitle': label_dict[final_result[i]],
                'startSlideIndex': i,
                'endSlideIndex': i
            })
        else :
            outline[-1]['endSlideIndex'] = i
    return outline, weights

def get_outline_dp_mask(section_data, top_sections, script_sentence_range, target_mask = None):
    label_dict = sorted(list(set(section_data)))

    for i, section in enumerate(label_dict):
        print(i, ":", section)

    n = len(label_dict)
    m = len(script_sentence_range)
    INF = (m + 1) * 100

    dp = [[(-INF, n, -1) for j in range(m)] for i in range(1 << n)]
    dp[0][0] = (0, n)

    for i in range(m):
        scores = [0 for k in range(n)]
        for j in range(i + 1, m):
            for top_section in top_sections[j]:
                pos = label_dict.index(top_section[0])
                scores[pos] += top_section[1]

            for mask in range(0, (1 << n)):
                if dp[mask][i][0] < 0:
                    continue
                for k in range (n):
                    if mask & (1 << k) > 0:
                        continue
                    nmask = mask | (1 << k)
                    if (dp[nmask][j][0] < dp[mask][i][0] + scores[k]):
                        dp[nmask][j] = (dp[mask][i][0] + scores[k], k, i)

    recover_mask = 0
    recover_slide_id = m - 1

    weights = [-1 for i in range(n + 1)]

    for mask in range(1 << n):
        cnt_segments = bin(mask).count('1')
        weights[cnt_segments] = max(weights[cnt_segments], dp[mask][recover_slide_id][0])

        if dp[mask][recover_slide_id][0] > dp[recover_mask][recover_slide_id][0]:
            recover_mask = mask
        if cnt_segments < bin(recover_mask).count('1') and dp[mask][recover_slide_id][0] == dp[recover_mask][recover_slide_id][0]:
            recover_mask = mask

    if target_mask is not None:
        recover_mask = target_mask
        print(bin(target_mask), bin(recover_mask), dp[target_mask][recover_slide_id][0])
    
    outline = []
    while recover_slide_id > 0:
        print(recover_mask, recover_slide_id, dp[recover_mask][recover_slide_id])
        section_id = dp[recover_mask][recover_slide_id][1]
        next_recover_mask = recover_mask ^ (1 << section_id)
        next_recover_slide_id = dp[recover_mask][recover_slide_id][2]
        outline.append({
            "sectionTitle": label_dict[section_id],
            "startSlideIndex": next_recover_slide_id + 1,
            "endSlideIndex": recover_slide_id,
        })
        recover_mask = next_recover_mask
        recover_slide_id = next_recover_slide_id
    
    return outline[::-1], weights

def get_outline_simple(top_sections):
    outline = []
    weights = []

    for i in range(1, len(top_sections)):
        scores = {
            "NO_SECTION": 0
        }
        for j in range(0, len(top_sections[i])):
            if top_sections[i][j][0] not in scores:
                scores[top_sections[i][j][0]] = 0    
            scores[top_sections[i][j][0]] = max(scores[top_sections[i][j][0]], top_sections[i][j][1])
        section = "NO_SECTION"
        for (k, v) in scores.items():
            if v > scores[section]:
                section = k
        outline.append({
            "sectionTitle": section,
            "startSlideIndex": i,
            "endSlideIndex": i,
        })
        weights.append(scores[section])
    return outline, weights

def get_outline_generic(outlining_approach, section_data, top_sections, script_sentence_range, target_mask = None):
    if outlining_approach == 'dp_mask':
        return get_outline_dp_mask(section_data, top_sections, script_sentence_range, target_mask)
    if outlining_approach == 'simple':
        return get_outline_simple(top_sections)
    
    return get_outline_dp(section_data, top_sections, script_sentence_range)

def add_sections_as_paragraphs(section_data, paper_data):
    ret_section_data = []
    ret_paper_data = []

    for i in range(0, len(section_data)):
        if i == 0 or section_data[i] != section_data[i - 1]:
            ret_section_data.append(section_data[i])
            ret_paper_data.append(section_data[i] + ".")
        ret_section_data.append(section_data[i])
        ret_paper_data.append(paper_data[i])
    return ret_section_data, ret_paper_data

def fix_section_titles(section_data, paper_data):
    ret_section_data = []
    ret_paper_data = []
    #cnt_title = 0

    last_section = None

    def is_main_section(title):
        if title[0] in digits or title.isupper() is True:
            return True
        return False

    for (section, paragraph) in zip(section_data, paper_data):
        if is_section_skipped(section):
            continue
        if is_main_section(section) or last_section is None:
            ret_section_data.append(section)
            ret_paper_data.append(paragraph)
            last_section = section
        else:
            ret_section_data.append(last_section)
            ret_paper_data.append(paragraph)

    return ret_section_data, ret_paper_data

def evaluate_outline(outline, gt_outline, slide_info):
    return {
        "boundariesAccuracy": 100,
        "timeAccuracy": 100,
        "structureAccuracy": 100,
        "mappingAccuracy": 100,
    }

def process(path, similarity_type, outlining_approach, apply_thresholding):
    timestamp = open(os.path.join(path, "frameTimestamp.txt"), "r")

    timestamp_data = []
    script_data = []

    paper_data = read_txt(os.path.join(path, "paperData.txt"))
    section_data = read_txt(os.path.join(path, "sectionData.txt"))
    script_data = read_txt(os.path.join(path, "scriptData.txt"))
    gt_data = read_json(os.path.join(path, "groundTruth.txt"))

    section_data, paper_data = add_sections_as_paragraphs(section_data, paper_data)

    section_data, paper_data = fix_section_titles(section_data, paper_data)

    while True :
        line = timestamp.readline()
        if not line :
            break
        timestamp_data.append([float(line.split('\t')[0]), float(line.split('\t')[1])])

    ocr_data = []
    for i in range(len(timestamp_data)) :
        ocr_file = open(os.path.join(path, "ocr", str(i) + ".jpg.txt"), "r")
        ocr_data.append('')
        first_line = False
        while True :
            line = ocr_file.readline()
            if not line :
                break
            if first_line is True:
                first_line = False
                continue
            res = line.split('\t')[-1].strip()
            if len(res) > 0 :
                ocr_data[-1] = ocr_data[-1] + ' ' + res
    
    result = {}

    result['title'] = "tempTitle"
    result['slideCnt'] = len(timestamp_data)
    result['slideInfo']= []
    result['groundTruthOutline'] = gt_data['groundTruthSegments']
    for i in range(len(timestamp_data)) :
        result['slideInfo'].append({
            "index": i,
            "startTime": timestamp_data[i][0],
            "endTime": timestamp_data[i][1],
            "script": script_data[i],
            "ocrResult": ocr_data[i],
        })
    

    _paper_data = []
    _script_data = []

    script_sentence_range = []
    for i, (script, ocr) in enumerate(zip(script_data, ocr_data)):
        # if (len(ret_script_data) > 10):
        #     break
        if (similarity_type == "classifier"):
            sentences = [script + " " + ocr]
        else:
            sentences = get_sentences(script)
            sentences.append(ocr)
        script_sentence_range.append(len(sentences))
        _script_data.extend(sentences)

    paper_sentence_id = []
    for i, paragraph in enumerate(paper_data):
        if (len(word_tokenize(paragraph)) < MIN_PARAGRAPH_LENGTH):
            continue
        # if (len(ret_paper_data) > 10):
        #     break
        sentences = get_sentences(paragraph)
        for j in range(len(_paper_data), len(sentences) + len(_paper_data)):
            paper_sentence_id.append(i)
        _paper_data.extend(sentences)

    print("Sentences# {} Scripts# {}".format(len(_script_data), len(script_data)))
    print("Sentences# {} Paragraphs# {}".format(len(_paper_data), len(paper_data)))

    if similarity_type == 'keywords':
        overall, top_sections, paper_keywords, script_keywords = get_similarity_keywords(
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, section_data, top_sections, script_sentence_range)

        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = script_keywords
        result["paperSentences"] = paper_keywords
    elif similarity_type == 'embeddings':
        overall, top_sections = get_similarity_embeddings(
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, section_data, top_sections, script_sentence_range)

        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = _script_data
        result["paperSentences"] = _paper_data
    elif similarity_type == "classifier":
        overall, top_sections, paper_data_by_section = get_similarity_classifier(
            _paper_data, _script_data, section_data, paper_sentence_id, script_sentence_range, apply_thresholding
        )
        outline, weights = get_outline_generic(outlining_approach, section_data, top_sections, script_sentence_range)
        
        result['topSections'] = top_sections
        result['outline'] = outline
        result['weights'] = weights
        result["similarityTable"] = numpy.float64(overall).tolist()
        result["scriptSentences"] = paper_data_by_section
        result["paperSentences"] = _script_data

    result["evaluationData"] = evaluate_outline(result["outline"], result["groundTruthOutline"], result["slideInfo"])

    json_file = open(os.path.join(path, "result.json"), "w")
    json_file.write(json.dumps(result))
    return result

if __name__ == "__main__":
    #output = process('./slideMeta/slideData/0', approach="classifier")
    output = process('./slideMeta/slideData/0', similarity_type="keywords", outlining_approach="dp_mask", apply_thresholding=False)
    #output = process('./slideMeta/slideData/0', approach="embeddings")
    print(output["outline"])
    print(len(output["topSections"][0]))