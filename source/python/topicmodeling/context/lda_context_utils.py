from gensim import corpora
from gensim.models import ldamodel, LdaMulticore
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
import numpy
from etl import ETLUtils
from utils.constants import Constants

__author__ = 'fpena'


def build_topic_model_from_documents(document_list):
    """
    Builds a topic model with the given documents. The model is built using
    Latent Dirichlet Allocation

    :type document_list: list[str]
    :parameter document_list: a list of strings, in which each element represnts
    a document
    :rtype: gensim.models.ldamodel.LdaModel
    :return: an LdaModel built using the reviews contained in the records
    parameter
    """

    bag_of_words = create_bag_of_words(document_list)

    dictionary = corpora.Dictionary(bag_of_words)
    dictionary.filter_extremes()
    corpus = \
        [dictionary.doc2bow(text) for text in bag_of_words]

    return build_topic_model_from_corpus(corpus, dictionary)


def build_topic_model_from_corpus(corpus, dictionary):
    """
    Builds a topic model with the given corpus and dictionary.
    The model is built using Latent Dirichlet Allocation

    :type corpus list
    :parameter corpus: a list of bag of words, each bag of words represents a
    document
    :type dictionary: gensim.corpora.Dictionary
    :parameter dictionary: a Dictionary object that contains the words that are
    permitted to belong to the document, words that are not in this dictionary
    will be ignored
    :rtype: gensim.models.ldamodel.LdaModel
    :return: an LdaModel built using the reviews contained in the records
    parameter
    """

    # numpy.random.seed(0)
    if Constants.LDA_MULTICORE:
        print('lda multicore')
        topic_model = LdaMulticore(
            corpus, id2word=dictionary,
            num_topics=Constants.LDA_NUM_TOPICS,
            passes=Constants.LDA_MODEL_PASSES,
            iterations=Constants.LDA_MODEL_ITERATIONS,
            workers=Constants.NUM_CORES - 1)
    else:
        print('lda monocore')
        topic_model = ldamodel.LdaModel(
            corpus, id2word=dictionary,
            num_topics=Constants.LDA_NUM_TOPICS,
            passes=Constants.LDA_MODEL_PASSES,
            iterations=Constants.LDA_MODEL_ITERATIONS)

    return topic_model


def update_reviews_with_topics(topic_model, corpus_list, reviews,
                               minimum_probability):
    """

    :type minimum_probability: float
    :param minimum_probability:
    :type topic_model: LdaModel
    :param topic_model:
    :type corpus_list: list
    :param reviews:
    """
    # print('reviews length', len(reviews))

    for review, corpus in zip(reviews, corpus_list):
        review[Constants.TOPICS_FIELD] =\
            topic_model.get_document_topics(corpus, minimum_probability)


def calculate_topic_weighted_frequency(topic, reviews):
    """

    :type topic: int
    :param topic:
    :type reviews: list[dict]
    :param reviews:
    :return:
    """
    num_reviews = 0.0

    for review in reviews:
        for review_topic in review[Constants.TOPICS_FIELD]:
            if topic == review_topic[0]:
                num_reviews += 1

    return num_reviews / len(reviews)


def calculate_topic_weighted_frequency_complete(topic, reviews):
    """

    :type topic: int
    :param topic:
    :type reviews: list[dict]
    :param reviews:
    :return:
    """
    review_frequency = 0.0
    log_words_frequency = 0.0
    log_past_verbs_frequency = 0.0

    for review in reviews:
        for review_topic in review[Constants.TOPICS_FIELD]:
            if topic == review_topic[0]:
                review_frequency += 1
                log_words_frequency += review['log_words']
                log_past_verbs_frequency += review['log_past_verbs']

    results = {
        'review_frequency': review_frequency / len(reviews),
        'log_words_frequency': log_words_frequency / len(reviews),
        'log_past_verbs_frequency': log_past_verbs_frequency / len(reviews)
    }

    return results


def discover_topics(text_reviews, num_topics):

    processed = create_bag_of_words(text_reviews)

    dictionary = corpora.Dictionary(processed)
    dictionary.filter_extremes(2, 0.6)

    # dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in processed]

    # I can print out the documents and which is the most probable topics for
    # each doc.
    lda_model =\
        ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=num_topics)
    # corpus_lda = lda_model[corpus]
    #
    # for l, t in izip(corpus_lda, corpus):
    #   print l, "#", t
    # for l in corpus_lda:
    #     print(l)
    # for topic in lda_model.show_topics(num_topics=num_topics, num_words=50):
    #     print(topic)

    return lda_model


def create_bag_of_words(document_list):
    """
    Creates a bag of words representation of the document list given. It removes
    the punctuation and the stop words.

    :type document_list: list[str]
    :param document_list:
    :rtype: list[list[str]]
    :return:
    """
    tokenizer = RegexpTokenizer(r'\w+')
    cached_stop_words = set(stopwords.words("english"))
    body = []
    processed = []

    # remove common words and tokenize
    # texts = [[word for word in document.lower().split()
    #           if word not in stopwords.words('english')]
    #          for document in reviews]

    for i in range(0, len(document_list)):
        body.append(document_list[i].lower())

    for entry in body:
        row = tokenizer.tokenize(entry)
        processed.append(
            [word for word in row if word not in cached_stop_words])

    return processed


def get_user_item_reviews(records, user_id, apply_filter=False):

    if apply_filter:
        user_records = ETLUtils.filter_records(records, 'user_id', [user_id])
    else:
        user_records = records

    if not user_records:
        return {}

    items_reviews = {}

    for record in user_records:
        items_reviews[record['offering_id']] = record['text']

    return items_reviews


def get_user_item_contexts(
        records, lda_model, user_id, apply_filter=False,
        minimum_probability=None):

    if apply_filter:
        user_records = ETLUtils.filter_records(records, 'user_id', [user_id])
    else:
        user_records = records

    if not user_records:
        return {}

    items_reviews = {}

    for record in user_records:
        review_text = record['text']
        context = get_topic_distribution(
            review_text, lda_model, minimum_probability)
        items_reviews[record['offering_id']] = context

    return items_reviews


def get_topic_distribution(review_text, lda_model, minimum_probability,
                           text_sampling_proportion=None):
        """

        :type review_text: str
        :type lda_model: LdaModel
        :type minimum_probability: float
        :type text_sampling_proportion: float
        :param text_sampling_proportion: a float in the range [0,1] that
        indicates the proportion of text that should be sampled from the review
         text. If None then all the review text is taken
        """
        review_bow = create_bag_of_words([review_text])

        if text_sampling_proportion is not None and len(review_bow[0]) > 0:

            num_words = int(text_sampling_proportion * len(review_bow[0]))
            review_bow = [
                numpy.random.choice(review_bow[0], num_words, replace=False)
            ]

        dictionary = corpora.Dictionary(review_bow)
        corpus = dictionary.doc2bow(review_bow[0])
        lda_corpus = lda_model.get_document_topics(
            corpus, minimum_probability=minimum_probability)

        topic_distribution = numpy.zeros(lda_model.num_topics)
        for pair in lda_corpus:
            topic_distribution[pair[0]] = pair[1]

        return topic_distribution


def export_topics(topic_model, topic_ratio_map):

    print('export topic model')

    file_name = Constants.DATASET_FOLDER + 'all_reviews_topic_model_' + \
        Constants.ITEM_TYPE + '_' + \
        str(Constants.LDA_NUM_TOPICS) + '_' + \
        str(Constants.LDA_MODEL_PASSES) + '_' + \
        str(Constants.LDA_MODEL_ITERATIONS) + '.csv'
    print(file_name)

    num_words = 10
    headers = [
        'topic_id',
        'ratio',
        'words_ratio',
        'past_verbs_ratio',
        'frq',
        'specific_frq',
        'generic_frq',
        'log_words',
        'specific_log_words',
        'generic_log_words',
        'log_past_verbs',
        'specific_log_past_verbs',
        'generic_log_past_verbs'
    ]

    for i in range(num_words):
        headers.append('word' + str(i))

    results = []

    for topic in range(topic_model.num_topics):
        result = {}
        result['topic_id'] = topic
        result['ratio'] = topic_ratio_map[topic]['ratio']
        result['words_ratio'] = topic_ratio_map[topic]['words_ratio']
        result['past_verbs_ratio'] = topic_ratio_map[topic]['past_verbs_ratio']
        result['frq'] = topic_ratio_map[topic]['weighted_frq']['review_frequency']
        result['specific_frq'] = topic_ratio_map[topic]['specific_weighted_frq']['review_frequency']
        result['generic_frq'] = topic_ratio_map[topic]['generic_weighted_frq']['review_frequency']
        result['log_words'] = topic_ratio_map[topic]['weighted_frq']['log_words_frequency']
        result['specific_log_words'] = topic_ratio_map[topic]['specific_weighted_frq']['log_words_frequency']
        result['generic_log_words'] = topic_ratio_map[topic]['generic_weighted_frq']['log_words_frequency']
        result['log_past_verbs'] = topic_ratio_map[topic]['weighted_frq']['log_past_verbs_frequency']
        result['specific_log_past_verbs'] = topic_ratio_map[topic]['specific_weighted_frq']['log_past_verbs_frequency']
        result['generic_log_past_verbs'] = topic_ratio_map[topic]['generic_weighted_frq']['log_past_verbs_frequency']
        result.update(split_topic(topic_model.print_topic(topic, topn=num_words), num_words))
        results.append(result)

    ETLUtils.save_csv_file(file_name, results, headers)


def export_all_topics(topic_model):

    print('export topic model')

    file_name = Constants.DATASET_FOLDER + 'generic_topic_model_' + \
        Constants.ITEM_TYPE + '_' + \
        str(Constants.LDA_NUM_TOPICS) + '_' + \
        str(Constants.LDA_MODEL_PASSES) + '_' + \
        str(Constants.LDA_MODEL_ITERATIONS) + '.csv'
    print(file_name)

    num_words = 10
    headers = [
        'topic_id'
    ]

    for i in range(num_words):
        headers.append('word' + str(i))

    results = []

    for topic in range(topic_model.num_topics):
        result = {}
        result['topic_id'] = topic
        result.update(split_topic(topic_model.print_topic(topic, topn=num_words), num_words))
        results.append(result)

    ETLUtils.save_csv_file(file_name, results, headers)


def split_topic(topic_string, num_words):
    """
    Splits a topic into dictionary containing each word

    :type topic_string: str
    :param topic_string:
    :param num_words:
    """

    words_dict = {}
    index = 0
    topic_words = topic_string.split(' + ')
    for word in topic_words:
        words_dict['word' + str(index)] = word
        index += 1

    return words_dict


my_documents = [
    "Human machine interface for lab abc computer applications",
    "A survey of user opinion of computer system response time",
    "The EPS user interface management system",
    "System and human system engineering testing of EPS",
    "Relation of user perceived response time to error measurement",
    "The generation of random binary unordered trees",
    "The intersection graph of paths in trees",
    "Graph minors IV Widths of trees and well quasi ordering",
    "Graph minors A survey"
]

# print(create_bag_of_words(my_documents))

# my_bag_of_words = create_bag_of_words(my_documents)
# my_topic_model = discover_topics(my_documents, 3)
# my_dictionary = corpora.Dictionary(my_bag_of_words)
# my_dictionary.filter_extremes(2, 0.6)
# my_corpus = [my_dictionary.doc2bow(text) for text in my_bag_of_words]
# print(my_topic_model[my_corpus])
# for t in my_topic_model[my_corpus]:
#     print(t)
