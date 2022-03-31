import numpy
import spacy
import re

from nltk.tokenize import sent_tokenize

from sentence_transformers import SentenceTransformer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity

from string import ascii_lowercase, punctuation, digits

from __init__ import sort_section_data, FREQ_WORDS_SECTION_TITLES

class Vectorizer(object):
    def __init__(self, method='tf-idf', ngram_range=(1, 4)):
        self.method = method
        self.vectorizer = None

        if method == 'tf-idf':
            self.vectorizer = TfidfVectorizer(ngram_range=ngram_range)
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
    
    def get_feature_names(self):
        if self.method == 'tf-idf':
            return self.vectorizer.get_feature_names_out().tolist()
        else:
            return []


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
    top_k_per_paragraph = 1

    overall = numpy.array(overall)

    top_paragraphs = []

    script_sentence_start = 0

    for i in range(len(script_sentence_range)):
        all_scores_per_paragraph = [[] for i in range(paper_sentence_id[-1] + 1)]
        section_scores = numpy.zeros(len(section_data), dtype=numpy.float64)
        for j in range(script_sentence_start, script_sentence_start + script_sentence_range[i]):
            args = numpy.argsort(overall[:, j])
            if apply_thresholding is True:
                args = args[-top_k:]
            for pos in args:
                score_to_add = overall[pos][j]

                # OCR Result
                if j == script_sentence_start + script_sentence_range[i] - 1:
                    score_to_add *= 2
                all_scores_per_paragraph[paper_sentence_id[pos]].append(score_to_add)
                #section_scores[paper_sentence_id[pos]] = max(score_to_add, section_scores[paper_sentence_id[pos]])
        
        for paragraph_id in range(len(all_scores_per_paragraph)):
            sorted_all_scores = sorted(all_scores_per_paragraph[paragraph_id], reverse=True)
            cur_top = min(len(sorted_all_scores), top_k_per_paragraph)
            cur_score = 0
            for k in range(cur_top):
                cur_score += sorted_all_scores[k]
            if cur_top > 0:
                cur_score /= cur_top
            section_scores[paragraph_id] = cur_score
        
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

    mx_score = 0

    for idx in range(len(top_sections)):
        for top_section in top_sections[idx]:
            mx_score = max(mx_score, top_section[1])
    
    if mx_score > 0:
        for idx in range(len(top_sections)):
            for j in range(len(top_sections[idx])):
                new_score = (top_sections[idx][j][0], top_sections[idx][j][1] / mx_score)
                top_sections[idx][j] = new_score
    return top_sections

def get_classifier_similarity(
    method,
    paper_data, script_data, section_data, paper_sentence_id, script_sentence_range,
    freq_words_per_section,
    apply_thresholding
):
    top_k = 5
    val_threshold = 0.1

    label_dict = sort_section_data(section_data)
    label_categories = [ label_dict.index(section_data[sentence_id]) for sentence_id in paper_sentence_id ]

    model = RandomForestClassifier()

    vectorizer = Vectorizer(method)
    X = vectorizer.fit_transform(list(map(preprocess_text, paper_data)))
    print(X.shape)

    Y = numpy.array(*[label_categories])
    print(Y.shape)

    model.fit(X, Y)

    def get_all_probs(t):
        if t == "":
            return [0.0 for i in range(len(label_dict))]
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

    
    mx_score = 0

    for idx in range(len(top_sections)):
        for top_section in top_sections[idx]:
            mx_score = max(mx_score, top_section[1])
    
    if mx_score > 0:
        for idx in range(len(top_sections)):
            for j in range(len(top_sections[idx])):
                new_score = (top_sections[idx][j][0], top_sections[idx][j][1] / mx_score)
                top_sections[idx][j] = new_score

    return overall, top_sections, paper_data_by_section

def get_cosine_similarity(
    method,
    paper_data, script_data, section_data, paper_sentence_id, script_sentence_range,
    freq_words_per_section,
    apply_thresholding
):
    vectorizer = Vectorizer(method=method)

    paper_embeddings = vectorizer.fit_transform(paper_data)
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

    script_start = 0

    for slide_idx in range(len(top_sections)):
        script_end = script_start + script_sentence_range[slide_idx]
        for top_section_idx, top_section in enumerate(top_sections[slide_idx]):
            improvements = 0
            title = top_section[0]
            rep_title = None
            for freq_titles in FREQ_WORDS_SECTION_TITLES:
                for freq_title in freq_titles:
                    if freq_title.lower() in title.lower():
                        rep_title = freq_titles[0]
                        break
                if rep_title is not None:
                    break
            if rep_title is None or FREQ_WORDS_SECTION_TITLES[0][0] == rep_title:
                continue
            for str_ngram in freq_words_per_section.keys():
                ngram = int(str_ngram)
                if ngram < 2:
                    continue
                total_ratios = 0
                total_freqs = 0
                for freq_entity in freq_words_per_section[str_ngram][rep_title]:
                    text = freq_entity["text"]
                    paper_ratio = freq_entity["ratio"]
                    corpus_freq = freq_entity["count"]

                    if paper_ratio == 1:
                        paper_ratio = 10
                    for script_idx in range(script_start, script_end):
                        if text in script_data[script_idx]:
                            total_ratios += paper_ratio
                            total_freqs += corpus_freq
                #top_sections[slide_idx][top_section_idx] = (top_section[0], top_section[1] + ngram * total_ratios)
                improvements += ngram * total_ratios
            if improvements > 0:
                print(slide_idx, top_section[0], ":", round(top_section[1], 2), round(improvements, 2))
        script_start = script_end
    return overall, top_sections


def get_keywords_similarity(
    method,
    paper_data, script_data, section_data, paper_sentence_id, script_sentence_range,
    freq_words_per_section,
    apply_thresholding
):
    nlp = spacy.load("en_core_web_sm")
    vectorizer = Vectorizer(method, (1, 1))

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
    vectorizer_features = vectorizer.get_feature_names()

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

def get_strong_similarity(
    method,
    paper_data, script_data, section_data, paper_sentence_id, script_sentence_range, transitions,
    freq_words_per_section
):
    nlp = spacy.load("en_core_web_sm")
    vectorizer = Vectorizer(method, (1, 1))

    overall = numpy.zeros((len(paper_data), len(script_data)))

    paper_keywords = []
    script_keywords = []
    
    for paper_sentence in paper_data:
        paper_keywords.append(get_keywords(paper_sentence, nlp))

    for script_sentence in script_data:
        script_keywords.append(get_keywords(script_sentence, nlp))

    LOL = vectorizer.fit_transform(map(' '.join, paper_keywords))
    vectorizer_features = vectorizer.get_feature_names()

    #print(LOL.shape, vectorizer_features)

    strong_mappings = [{} for i in range(len(script_sentence_range))]

    for j in range(len(script_keywords)):
        X = vectorizer.transform([' '.join(script_keywords[j])])
        #unique_keywords = list(set(script_keywords[j]))
        unique_keywords = list(script_keywords[j])
        
        if len(unique_keywords) == 0:
                continue
        score_for_each = []
        total_score = 0
        for word in unique_keywords:
            # score_for_each.append(1)
            # total_score += 1
            # continue
            try:
                score_for_each.append(1.0 - X[0, vectorizer_features.index(word)])
            except:
                score_for_each.append(0.0)
            total_score += score_for_each[-1]

        if total_score < 2.5:
            print("Skipped: ", j, " - ", total_score, ":", script_data[j])
            continue

        # if total_score < 5:
        #     print("Skipped: ", j, " - ", total_score, ":", script_data[j])
        #     continue

        for i in range(len(paper_keywords)):
            for k, word in enumerate(unique_keywords):
                if word in paper_keywords[i]:
                    overall[i][j] += score_for_each[k]
            overall[i][j] /= total_score

        slide_idx = 0
        sentence_cnt = j

        while (slide_idx < len(script_sentence_range) and sentence_cnt > 0):
            sentence_cnt -= script_sentence_range[slide_idx]
            if sentence_cnt < 0:
                break
            slide_idx += 1

        if sentence_cnt == -1:
            print(slide_idx, ":", script_data[j])

        for i in range(len(paper_keywords)):
            section_title = section_data[paper_sentence_id[i]]
            if overall[i][j] > 0.3:
                if section_title not in strong_mappings[slide_idx]:
                    strong_mappings[slide_idx][section_title] = 0
                strong_mappings[slide_idx][section_title] += overall[i][j]

    with open("./experiments_similarity.csv", "w") as f:
        print("title", end=",", file=f)
        for idx in range(1, len(transitions)):
            print(str(transitions[idx - 1] + 1) + "-" + str(transitions[idx]), end=",", file=f)
        print("", file=f)

        rev_strong_mappings = {}

        label_dict = sort_section_data(section_data)

        for label in label_dict:
            rev_strong_mappings[label] = []

        for slide_idx in range(1, len(script_sentence_range)):

            scores = strong_mappings[slide_idx].values()
            scores = sorted(scores)

            for key in rev_strong_mappings.keys():
                if key in strong_mappings[slide_idx]:
                    rank = len(scores)
                    while rank > 1 and scores[rank - 1] > strong_mappings[slide_idx][key]:
                        rank -= 1
                    rev_strong_mappings[key].append(strong_mappings[slide_idx][key])
                else:
                    rev_strong_mappings[key].append(0)
                #break
                #if "introduction" in key.lower() or "related" in key.lower() or "conclusion" in key.lower() or "discussion" in key.lower():
                #    print("\t", key, ":", val)
                #    break
        for label in label_dict:
            print(label, ":", rev_strong_mappings[label])
            print(label, end=",", file=f)
            for val in rev_strong_mappings[label]:
                print(round(val, 2), end=",", file=f)
            print("", file=f)
            
    top_sections = get_top_sections(overall, section_data, script_sentence_range, paper_sentence_id, False, 10)
    
    return overall, top_sections, paper_keywords, script_keywords