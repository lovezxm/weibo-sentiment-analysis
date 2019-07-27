# coding=utf-8
import re
import os
import numpy as np
import pandas as pd
import linecache
import random
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

# Keras
import tensorflow as tf
import keras.backend.tensorflow_backend as KTF
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model

from scripts.attention.layers import AttentionLayer


### set GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
KTF.set_session(session)

data = pd.read_csv('./data/twitter/cleaned_tweets_text_10W.csv')
data.cleaned_text = data.cleaned_text.astype(str)

MAX_NB_WORDS = 50000
DROPOUT = 0.5
MAX_LENGTH = 35

tokenizer = Tokenizer(num_words=MAX_NB_WORDS, filters='')
tokenizer.fit_on_texts(data['cleaned_text'])
logging.info('twitter tokenizer loaded ......')


def get_index2word():
    """Computes the table that maps ids to their words."""
    word2index = tokenizer.word_index
    index2word = {v: k for k, v in word2index.items()}
    return index2word


def reconstruct(sample, index2word):
    """Given a list of word ids, returns a list of words."""
    list = []
    for word in sample:
        try:
            word = index2word[word]
        except:
            word = '[PAD]'

        list.append(word)
    return list


def _weight2color(brightness):
    """Converts a single (positive) attention weight to a shade of blue."""
    brightness = brightness.item()

    brightness = int(round(255 * brightness))  # convert from 0.0-1.0 to 0-255
    ints = (255 - brightness, 255 - brightness, 255)
    return 'rgba({}, {}, {}, 0.6)'.format(*ints)


def print_sentence(sentence, weights):
    """Prints a sample (sequence) making the most attended words background darker."""
    parts = list()
    for word, weight in zip(sentence, weights):
        if word == '[PAD]':
            break
        parts.append('<span style="background: {}; color:#000; padding:2px; font-weight=\'bold\'">{}</span>'.format(
            _weight2color(weight), word))

    text = ' '.join(parts)
    return text


index2word = get_index2word()
index2label = {
    0: '消极',
    1: '积极'
}

best_model = load_model('./models/twitter/BGRU-Attetnion-0.8079.hdf5',
                        custom_objects={"AttentionLayer": AttentionLayer})
viz_model = load_model('./models/twitter/BGRU-Attetnion-0.8079-viz.hdf5',
                       custom_objects={"AttentionLayer": AttentionLayer})
logging.info('twitter Model loaded ......')


def preprocess_word(word):
    # Remove punctuation
    word = word.strip('\'"():')
    # Convert more than 2 letter repetitions to 2 letter
    # funnnnny --> funny
    word = re.sub(r'(.)\1+', r'\1\1', word)
    # Remove - & '
    word = re.sub(r'(-|\')', '', word)
    return word


def is_valid_word(word):
    # Check if word begins with an alphabet
    if (re.search(r'^[a-zA-Z][a-z0-9A-Z\._]*$',
                  word) is not None) or word == '.' or word == '?' or word == '!' or word == ',' or word == ';':
        return True
    return False


def handle_emojis(tweet):
    # Smile -- :), : ), :-), (:, ( :, (-:, :')
    tweet = re.sub(r'(:\s?\)|:-\)|\(\s?:|\(-:|:\'\))', ' EMO_POS ', tweet)
    # Laugh -- :D, : D, :-D, xD, x-D, XD, X-D
    tweet = re.sub(r'(:\s?D|:-D|x-?D|X-?D)', ' EMO_POS ', tweet)
    # Love -- <3, :*
    tweet = re.sub(r'(<3|:\*)', ' EMO_POS ', tweet)
    # Wink -- ;-), ;), ;-D, ;D, (;,  (-;
    tweet = re.sub(r'(;-?\)|;-?D|\(-?;)', ' EMO_POS ', tweet)
    # Sad -- :-(, : (, :(, ):, )-:
    tweet = re.sub(r'(:\s?\(|:-\(|\)\s?:|\)-:)', ' EMO_NEG ', tweet)
    # Cry -- :,(, :'(, :"(
    tweet = re.sub(r'(:,\(|:\'\(|:"\()', ' EMO_NEG ', tweet)
    return tweet


def preprocess_tweet(tweet):
    processed_tweet = []
    # Convert to lower case
    tweet = tweet.lower()
    # Replaces URLs with the word URL
    tweet = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', ' URL ', tweet)
    # Replace @handle with the word USER_MENTION
    tweet = re.sub(r'@[\S]+', ' USER_MENTION ', tweet)
    # Replaces #hashtag with hashtag
    tweet = re.sub(r'#(\S+)', ' TOPIC ', tweet)
    # Remove RT (retweet)
    tweet = re.sub(r'\brt\b', '', tweet)

    # Strip space, " and ' from tweet
    tweet = tweet.strip(' "\'')
    # Replace emojis with either EMO_POS or EMO_NEG
    tweet = handle_emojis(tweet)
    # Replace multiple spaces with a single space
    tweet = re.sub(r'\s+', ' ', tweet)

    # Replace 1+ dots with dot
    tweet = re.sub(r'\.{1,}', ' .', tweet)
    tweet = re.sub(r'\?{1,}', ' ?', tweet)
    tweet = re.sub(r'\!{1,}', ' !', tweet)
    tweet = re.sub(r'\,{1,}', ' ,', tweet)
    tweet = re.sub(r'\;{1,}', ' ;', tweet)

    words = tweet.split()
    for word in words:
        word = preprocess_word(word)
        if is_valid_word(word):
            processed_tweet.append(word)

    return ' '.join(processed_tweet)


def predict_emotion(str):
    logging.debug("predictEmotion:text:" + str)
    processed_str = preprocess_tweet(str)
    logging.debug("processed_str:" + processed_str)
    processed_str_list = [processed_str]
    sequences_str = tokenizer.texts_to_sequences(processed_str_list)
    logging.debug("sequences_str:" )
    logging.debug(sequences_str[0])
    str_len = len(sequences_str[0])
    padded_sequences_str = pad_sequences(sequences_str, maxlen=MAX_LENGTH, padding='post', truncating='post')
    logging.debug("padded_sequences_str:" )
    logging.debug(padded_sequences_str[0])
    index = 0
    words = reconstruct(padded_sequences_str[index], index2word)
    sample = padded_sequences_str[index:index + 1]

    # getting prediction and alphas
    positive_percent = best_model.predict(sample)[0]
    pred = int(positive_percent >= 0.5)
    z = viz_model.predict(sample)[0]
    # reescaling for visualization purposes
    w = (z - np.min(z)) / (np.max(z) - np.min(z))
    # ta-da
    result = {}
    result['word_score'] = z.tolist()
    result['predict'] = index2label[pred]
    result['actual'] = ""
    result['positive_percent'] = round(float(positive_percent), 2)
    result['print_sentence'] = print_sentence(words, w)
    return result


def predict_emotion_random():
    # 从测试集文件中随机读取一行
    a = random.randrange(2, 10000)  # 2-10000中生成随机数
    theline = linecache.getline(r'./data/twitter/test-data-1W.csv', a)
    tweet_lable = int(theline[:1])
    tweet = theline[2:]
    result = {}
    result = predict_emotion(tweet)
    result['input_text'] = tweet
    result['actual'] = index2label[tweet_lable]
    return result

