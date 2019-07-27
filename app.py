# coding=utf-8

# Flask utils
from flask import Flask, redirect, url_for, request, render_template,Response, json
from gevent.pywsgi import WSGIServer
from scripts import twitterOps
from scripts import weiboOps

import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)


# Define a flask app
app = Flask(__name__,template_folder="")


@app.route('/', methods=['GET'])
def index():
    # Main page
    logging.info("return main page")
    return render_template('index.html')


@app.route('/weibo', methods=['GET'])
def indexweibo():
    # Main page
    logging.info("return main weibo page")
    return render_template('indexweibo.html')


@app.route('/predict', methods=['POST'])
def predict():
    # Get the json from post request
    req_data = request.get_json()
    logging.debug(req_data)
    type = 'twitter'
    input_text = None
    if 'type' in req_data:
        type = req_data['type']
    if 'input_text' in req_data:
        input_text = req_data['input_text']

    result = {}
    if input_text is not None and type == 'twitter':
        result = twitterOps.predict_emotion(input_text)
    elif input_text is not None and type == 'weibo':
        result = weiboOps.predict_emotion(input_text)
    elif input_text is None and type == 'twitter_random':
        result = twitterOps.predict_emotion_random()
    elif input_text is None and type == 'weibo_random':
        result = weiboOps.predict_emotion_random()

    result['type'] = type
    logging.debug("result:")
    logging.debug(result)
    res = Response(json.dumps(result), content_type='application/json')
    return res



if __name__ == '__main__':
    # app.run(port=5001, debug=True)

    # Serve the app with gevent
    http_server = WSGIServer(('', 5001), app)
    logging.info("server started......")
    http_server.serve_forever()

