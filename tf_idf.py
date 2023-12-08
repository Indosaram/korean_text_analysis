from math import log

import pandas as pd


def tf(t, d):
    return d.count(t)


def idf(term, docs):
    df = sum(term in doc for doc in docs)
    n = len(docs)
    return log(n / (df + 1))


def tf_idf(terms, docs):
    idfs = [idf(term, docs) for term in terms]
    tfidf = []
    for doc in docs:
        doc_tfidf = []
        for term, _idf in zip(terms, idfs):
            _tf = doc.count(term)
            doc_tfidf.append(_tf * _idf)
        tfidf.append(doc_tfidf)

    return pd.DataFrame(tfidf, columns=terms)
