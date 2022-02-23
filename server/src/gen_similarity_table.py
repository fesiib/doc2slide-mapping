import numpy
import spacy
import re

from nltk.tokenize import sent_tokenize

from sentence_transformers import SentenceTransformer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity

from string import ascii_lowercase, punctuation, digits


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