# coding=utf-8
import re
import numpy as np
import pandas as pd
import linecache
import random
import pynlpir
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)

# Keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model


test_data = pd.read_csv("./data/weibo/test_use_t.csv", delimiter="\t")
train_data = pd.read_csv("./data/weibo/train_use_t.csv", delimiter="\t")

X_train = np.array(list(train_data['text']))
X_test = np.array(list(test_data['text']))

MAX_NB_WORDS = 40000
MAX_LENGTH = 108  # 此数字为 每条文本的平均单词数+2倍标准差
tokenizer = Tokenizer(num_words=MAX_NB_WORDS)  # 根据词频保留最大的前40000个词，其实总共也就 44325
tokenizer.fit_on_texts(np.concatenate((X_train, X_test), axis=0))
logging.info('weibo tokenizer loaded ......')

model_L1 = load_model('./models/weibo/L1-object-subject-0.7218.hdf5')
model_L2 = load_model('./models/weibo/L2-negative-positive-0.8632.hdf5')
model_L3negative = load_model('./models/weibo/L3negative-fear-anger-sadness-disgust-surprise-0.6197.hdf5')
model_L3positive = load_model('./models/weibo/L3positive-happy-like-0.8131.hdf5')
logging.info('weibo Model loaded ......')


def preprocess_weibo(tweet):
    processed_tweet = []
    # Replaces URLs with the word [URL]
    tweet = re.sub(r'(https?|ftp|file|www\.)[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', '[URL]', tweet)
    # Replaces Email with the word [URL]
    tweet = re.sub(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+[\.][a-zA-Z0-9_-]+', '[URL]', tweet)
    # Replaces @Bella6小7: 转发微博  with the word [FORWARD]
    tweet = re.sub(r'@[\S]+: 转发微博', '[FORWARD]', tweet)
    tweet = re.sub(r'@[\S]+:转发微博', '[FORWARD]', tweet)
    tweet = re.sub(r'@[\S]+：转发微博', '[FORWARD]', tweet)
    # Replaces 数字  with the word [N]
    tweet = re.sub(r'\d+', '[N]', tweet)
    # Replace 2+ dots with space
    tweet = re.sub(r'[\.。…]{2,}', '。', tweet)
    # Replace 2+ ~~ 为 ~
    tweet = re.sub(r'~{2,}', '~', tweet)
    # Replace 2+ 叹号 为 一个叹号
    tweet = re.sub(r'[!！]{2,}', '!', tweet)
    # Replace 2+ 叹号 为 一个叹号
    tweet = re.sub(r'[？?]{2,}', '?', tweet)
    # 去掉 //
    tweet = re.sub(r'//', ' ', tweet)
    # 去掉 引号
    tweet = re.sub(r'["“”\'‘’]', '', tweet)

    pynlpir.open(encoding='utf_8', encoding_errors='ignore')
    segments = pynlpir.segment(tweet, pos_tagging=False)
    i = 1
    count = len(segments) - 1
    for segment in segments:
        if re.match(r'\s+', segment):  # 过滤掉空格
            i = i + 1
            continue
        segment = re.sub(r'@[\S]+', '[USER_MENTION]', segment)
        processed_tweet.append(segment.strip())
        if (i == count) & (segment == '[USER_MENTION]'):  # 过滤掉最后一个单独的字
            break
        i = i + 1
    pynlpir.close()
    return ' '.join(processed_tweet)


L1_index2label = {
    0: '客观',
    1: '主观'
}
L2_index2label = {
    0: '消极',
    1: '积极'
}
L3negative_index2label = {
    0: '害怕',
    1: '生气',
    2: '伤心',
    3: '厌恶',
    4: '吃惊'
}
L3positive_index2label = {
    0: '高兴',
    1: '喜欢'
}
labelenglish2chinese = {
    'none': '客观',
    'fear': '害怕',
    'anger': '生气',
    'sadness': '伤心',
    'disgust': '厌恶',
    'surprise': '吃惊',
    'happiness': '高兴',
    'like': '喜欢'
}

def predict_emotion(str):
    logging.debug("predictEmotion:text:" + str)
    processed_str = preprocess_weibo(str)
    logging.debug("processed_str:" + processed_str)
    processed_str_list = [processed_str]
    sequences_str = tokenizer.texts_to_sequences(processed_str_list)
    logging.debug("sequences_str:")
    logging.debug(sequences_str[0])
    padded_sequences_str = pad_sequences(sequences_str, maxlen=MAX_LENGTH)
    logging.debug("padded_sequences_str:")
    logging.debug(padded_sequences_str[0])

    result = {}
    result['print_sentence'] = processed_str

    subject_percent = model_L1.predict(padded_sequences_str)[0]
    pred_L1 = int(subject_percent >= 0.5)
    result['pred_L1'] = L1_index2label[pred_L1]
    result['subject_percent'] = round(float(subject_percent), 2)
    if pred_L1 == 0:
        result['pred_L2'] = ''
        result['pred_L3'] = ''
        return result

    positive_percent = model_L2.predict(padded_sequences_str)[0]
    pred_L2 = int(positive_percent >= 0.5)
    result['pred_L2'] = L2_index2label[pred_L2]
    result['positive_percent'] = round(float(positive_percent), 2)
    if pred_L2 == 0:
        # 消极情感，进行消极细粒度分类
        negative_precent_list = model_L3negative.predict(padded_sequences_str)[0].tolist()
        pred_L3 = negative_precent_list.index(max(negative_precent_list))
        result['pred_L3'] = L3negative_index2label[pred_L3]
        result['negative_precent_list'] = negative_precent_list
    else:
        # 积极情感，进行积极细粒度分类
        like_precent = model_L3positive.predict(padded_sequences_str)[0]
        pred_L3 = int(like_precent >= 0.5)
        result['pred_L3'] = L3positive_index2label[pred_L3]
        result['like_precent'] = round(float(like_precent), 2)

    return result


def predict_emotion_random():
    a = random.randrange(1, 50)  # 1-50中生成随机数
    logging.debug("random_num" + str(a))
    line = linecache.getline(r'./data/weibo/test_original.csv', a)
    tweet_id = line[:line.find(',')]
    line = line[1 + line.find(','):]
    tweet_lable = line[:line.find(',')]
    tweet = line[1 + line.find(','):]
    result = {}
    result = predict_emotion(tweet)
    result['input_text'] = tweet
    result['actual'] = labelenglish2chinese[tweet_lable]
    return result


