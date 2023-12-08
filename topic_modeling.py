import pyLDAvis.gensim_models
from gensim import corpora, models
from gensim.models import CoherenceModel
from networkx import (bipartite_layout, circular_layout, kamada_kawai_layout,
                      planar_layout, random_layout, shell_layout,
                      spectral_layout, spiral_layout, spring_layout)


class TopicModeling:
    def __init__(self, texts):
        self.texts = texts
        self.dictionary = corpora.Dictionary(texts)
        self.corpus = [self.dictionary.doc2bow(text) for text in texts]

    def train_lda(self, num_topics=10, passes=15):
        return models.LdaModel(
            corpus=self.corpus,
            num_topics=num_topics,
            id2word=self.dictionary,
            passes=passes,
        )

    def get_topics(self, model, num_words=5):
        return model.print_topics(num_words=num_words)

    def compute_coherence(self, model):
        coherence_model = CoherenceModel(
            model=model, texts=self.texts, dictionary=self.dictionary, coherence="c_v"
        )
        return coherence_model.get_coherence()

    def compute_perplexity(self, model):
        return model.log_perplexity(self.corpus)

    def visualize(self, model):
        visualization = pyLDAvis.gensim_models.prepare(
            model, self.corpus, self.dictionary
        )
        pyLDAvis.display(visualization)
