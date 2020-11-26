import re
import json
import pymongo
import requests
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import numpy as np
from datetime import datetime
from threading import Thread

address="mongodb://aman:aman%40123@52.170.157.100:27017/hashtags?authSource=hashtags"
client = pymongo.MongoClient(address)
hashtags_db = client.get_database("hashtags")
new_words_col = hashtags_db['new_words_from_users']
popular_hashtag = hashtags_db['popular_keyword_hashtag']
popular_caption = hashtags_db['popular_keyword_caption']

# generic functions
def generate_ngrams(s, n):
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    tokens = [token for token in s.split(" ") if token != ""]
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]

def find_related_word_api(keyword, limit = 2):
    url = "https://relatedwords.org/api/related?term={}".format(keyword)
    try:
        result = requests.get(url).json()
        return [word_dict['word'] for word_dict in result[:limit]]
    except Exception as e:
        return []

def format_new_words(new_words):
    documents = []
    for new_word in list(new_words):
        document = {
                    'keyword' : new_word,
                    'createdAt' : datetime.now(),
                    'updatedAt' : datetime.now()
                }
        documents.append(document)
    return documents

# hashtag functions
def create_ngrams_list_hashtags(sentence):
    trigrams = generate_ngrams(sentence, 3)
    bigrams = generate_ngrams(sentence, 2)
    unigrams = generate_ngrams(sentence, 1)
    return list(set([' '.join(gram.split()) for gram in trigrams])) + \
            list(set([' '.join(gram.split()) for gram in bigrams])) + \
            list(set([' '.join(gram.split()) for gram in unigrams]))

def get_hashtags_from_keywords(list_keywords, lower_hashtag_keywords, size = 10, show_post_count = False, tags_per_set = 30):
    try:
        cursor = popular_hashtag.find({'keyword' : {'$in' : list_keywords}}, 
                                    {'_id' : 0, 'hashtags' : 1, 'keyword' : 1})
        hashtag_docs = [doc for doc in cursor]

        sorted_hashtag_docs = sorted(hashtag_docs, key = lambda doc : doc['keyword'].count(' '), reverse = True)
        fetched_sorted_keywords = [doc['keyword'] for doc in sorted_hashtag_docs]
        if fetched_sorted_keywords[0].count(' ') >= 1 and len(sorted_hashtag_docs[0]['hashtags']) >= 2 * tags_per_set:
            all_hashtag_list = sorted_hashtag_docs[0]['hashtags']
        else:
            all_hashtag_list = sum([doc['hashtags'] for doc in sorted_hashtag_docs], [])

        tag2posts = {hashtag['tag'] : hashtag['total_posts'] for hashtag in all_hashtag_list}
        
        if tag2posts:

            all_posts_count = list(tag2posts.values())
            normal_probs = np.array(all_posts_count) / sum(all_posts_count)
        
            if len(tag2posts.keys()) >= 2 * tags_per_set:
                hashtag_list = [list(np.random.choice(list(tag2posts.keys()), tags_per_set, False)) for i in range(size)]
            else:
                try:
                    hashtag_list = [list(np.random.choice(list(tag2posts.keys()), tags_per_set, False))]
                except Exception as e:
                    hashtag_list = []
        else:
            hashtag_list = []

        # storing new words (if any) in the new_words_from_users collection
        try:
            words = [doc['keyword'] for doc in hashtag_docs]
            new_words = set(lower_hashtag_keywords).difference(set(words))
            if new_words:
                documents = format_new_words(new_words)
                for document in documents:
                    try:
                        new_words_col.insert_one(document)
                    except Exception as e:
                        pass
        except Exception as e:
            pass
        if show_post_count:
            hashtag_list = [[[hashtag, tag2posts[hashtag]] for hashtag in hashtag_set] for hashtag_set in hashtag_list]
    except Exception as e:
        hashtag_list = []
    return hashtag_list

def produce_hashtags(list_keywords, hashtag_captions_dict, size = 10, show_post_count = False, tags_per_set = 30):
    if not list_keywords:
        hashtag_captions_dict['hashtags'] = []
        return
    lower_hashtag_keywords = list(map(str.lower, list_keywords))
    sentence = ' '.join(lower_hashtag_keywords)
    n_grams_hashtag_keywords = create_ngrams_list_hashtags(sentence)
    try:
        hashtag_list = get_hashtags_from_keywords(n_grams_hashtag_keywords, lower_hashtag_keywords, size = size, show_post_count = show_post_count, tags_per_set = tags_per_set)
        if hashtag_list:
            hashtag_captions_dict['hashtags'] = hashtag_list
        else:
            related_keywords = list(set(sum([find_related_word_api(keyword) for keyword in lower_hashtag_keywords], [])))
            hashtag_list = get_hashtags_from_keywords(related_keywords, lower_hashtag_keywords, size = size, show_post_count = show_post_count, tags_per_set = tags_per_set)
            if hashtag_list:
                hashtag_captions_dict['hashtags'] = hashtag_list
            else:
                hashtag_captions_dict['hashtags'] = []
    except Exception as e:
        hashtag_captions_dict['hashtags'] = []

# caption functions
def create_ngrams_list_captions(sentence):
    trigrams = generate_ngrams(sentence, 3)
    bigrams = generate_ngrams(sentence, 2)
    unigrams = generate_ngrams(sentence, 1)
    return list(set([' '.join(gram.split()) for gram in trigrams])) + \
            list(set([' '.join(gram.split()) for gram in bigrams])) + \
            list(set([' '.join(gram.split()) for gram in unigrams]))

def produce_captions_from_mongo(list_keywords, size = 10):
    try:
        cursor = popular_caption.find({'keyword' : {'$in' : list_keywords}}, {'_id' : 0, 'keyword' : 1, 'captions' : 1})
        caption_docs = [doc for doc in cursor]

        sorted_caption_docs = sorted(caption_docs, key = lambda doc : doc['keyword'].count(' '), reverse = True)
        fetched_sorted_keywords = [doc['keyword'] for doc in sorted_caption_docs]
        if fetched_sorted_keywords[0].count(' ') >= 1 and len(sorted_caption_docs[0]['captions']) >= size:
            all_captions_list = sorted_caption_docs[0]['captions']
        else:
            all_captions_list = sum([doc['captions'] for doc in sorted_caption_docs], [])

        if all_captions_list:
            try:
                mongo_captions_list = list(np.random.choice(all_captions_list, size, False))
            except:
                mongo_captions_list = []
        else:
            mongo_captions_list = []
    except Exception as e:
        print(e)
        mongo_captions_list = []
    return mongo_captions_list

def produce_captions_from_elastic(list_keywords, size = 10, elastic_endpoint = 'https://hash.apyhi.com/v0/es-caption'):
    try:
        query_input = ' '.join(list_keywords)
        url = elastic_endpoint + "?query_input=" + query_input + '&size=' + str(size)
        captions = requests.get(url).json()
        elastic_captions_list = captions
    except Exception as e:
        elastic_captions_list = []
    return elastic_captions_list

def produce_captions(list_keywords, hashtag_captions_dict, size = 10, elastic_endpoint = 'https://hash.apyhi.com/v0/es-caption'):
    if not list_keywords:
        hashtag_captions_dict['captions'] = []
        return
    try:
        lower_caption_keywords = list(map(str.lower, list_keywords))
        sentence = ' '.join(lower_caption_keywords)
        n_grams_caption_keywords = create_ngrams_list_captions(sentence)
        captions_list = []
        # Getting captions from Mongo first
        try:
            captions_list += produce_captions_from_mongo(n_grams_caption_keywords, size = size)
        except Exception as e:
            print(e)
            pass
        if len(captions_list) < size:
            # Getting captions from Elastic Search Service
            try:
                remaining_captions_size = size - len(captions_list)
                captions_list += produce_captions_from_elastic(lower_caption_keywords, remaining_captions_size, elastic_endpoint)
            except Exception as e:
                pass
        hashtag_captions_dict['captions'] = captions_list
    except Exception as e:
        hashtag_captions_dict['captions'] = []

# driver functions
def generate(list_keywords, size, show_post_count, show_captions, elastic_endpoint = 'https://hash.apyhi.com/v0/es-caption'):
    try:
        hashtag_captions_dict = {}
        hashtags_thread = Thread(target = produce_hashtags, args = (list_keywords,
                                                                    hashtag_captions_dict,
                                                                    size,
                                                                    show_post_count,
                                                                    30))
        hashtags_thread.start()
        if show_captions:
            captions_thread = Thread(target = produce_captions, args = (list_keywords,
                                                                        hashtag_captions_dict,
                                                                        size,
                                                                        elastic_endpoint))
            captions_thread.start()
            captions_thread.join()
        hashtags_thread.join()
        if hashtag_captions_dict:
            return hashtag_captions_dict
        else:
            return {}
    except Exception as e:
        return {}

def lambda_handler(event, context):
    try:
        keywords = event['queryStringParameters']['keywords'].strip('[]').split(',')
    except Exception as e:
        return {
            'statusCode': 200,
            'body': json.dumps("Missing parameter 'keywords'.")
        }
    try:
        show_post_count = True if "True" == event['queryStringParameters']['show_post_count'] else False
    except Exception as e:
        show_post_count = False
    try:
        size = int(event['queryStringParameters']['size'])
    except Exception as e:
        size = 10
    try:
        show_captions = True if "True" == event['queryStringParameters']['show_captions'] else False
    except Exception as e:
        show_captions = False
    elastic_endpoint = 'https://hash.apyhi.com/v0/es-caption' # not a param
    hashtag_captions_dict = generate(list_keywords = keywords,
                                    size = size,
                                    show_post_count = show_post_count,
                                    show_captions = show_captions,
                                    elastic_endpoint = elastic_endpoint)
    return {
        'statusCode': 200,
        'body': json.dumps(hashtag_captions_dict)
    }
    
if __name__ == "__main__":

    list_keywords = ['young' , 'adult'] # param
    size = 10 # param
    show_post_count = False # param
    show_captions = True # param
    elastic_endpoint = 'https://hash.apyhi.com/v0/es-caption' # not a param

    hashtag_captions_dict = generate(list_keywords = list_keywords,
                                    size = size, 
                                    show_post_count = show_post_count, 
                                    show_captions = show_captions,
                                    elastic_endpoint = elastic_endpoint)

    print(hashtag_captions_dict)