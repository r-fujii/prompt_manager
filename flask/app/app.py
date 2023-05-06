import os
import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, session

from chatbot import Chatbot

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.INFO) 
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
app.logger.addHandler(handler)

chatbot = Chatbot()


@app.route('/')
def index():
    app.logger.info('redirect to /prompt')
    return redirect(url_for('prompt'))

@app.route('/prompt')
def prompt():
    app.logger.info('get /prompt')
    # open setting modal if init_flg is True
    init_flg = any(item not in session for item in {'common_settings', 'temperature'})
    return render_template('prompt.html', init_flg=init_flg)

@app.route('/stats')
def stats():
    app.logger.info('get /stats')
    return render_template('stats.html')

@app.route('/_api/message', methods=['POST'])
def post_messages():
    app.logger.info('start post /_api/message')
    try:
        payload = request.json
        id2prompt = payload['id2prompt']
        user_message = payload['user_message']

        common_settings = session.get('common_settings', '')
        temperature = session.get('temperature', 1.0)

        app.logger.debug(f'id2prompt: {id2prompt}, user_message: {user_message}, common_settings: {common_settings}, temperature: {temperature}')
        res = chatbot.get_multiple_response(id2prompt, user_message, common_settings, temperature)
        app.logger.debug(f'res: {res}')

        app.logger.info('finish post /_api/message')
        return jsonify({'status': 'success', 'message': res})
    except:
        app.logger.error('failed post /_api/message')
        abort(500)

@app.route('/_api/count', methods=['POST'])
def count_tokens():
    app.logger.info('start post /_api/count')
    try:
        payload = request.json
        message = payload['prompt']

        app.logger.debug(f'message: {message}')
        num_tokens = chatbot.count_tokens(message)
        app.logger.debug(f'num_tokens: {num_tokens}')

        app.logger.info('finish post /_api/count')
        return jsonify({'status': 'success', 'num_tokens': num_tokens})
    except:
        app.logger.error('failed post /_api/count')
        abort(500)

@app.route('/_api/stats', methods=['POST'])
def get_stats():
    app.logger.info('start post /_api/stats')
    try:
        payload = request.json
        id2prompt = payload['id2prompt']
        user_message = payload['user_message']

        common_settings = session.get('common_settings', '')
        temperature = session.get('temperature', 1.0)

        app.logger.debug(f'id2prompt: {id2prompt}, user_message: {user_message}, common_settings: {common_settings}, temperature: {temperature}')
        user_message, prompt_completions_dict, metric_values = chatbot.get_stats(id2prompt, user_message, common_settings, temperature)
        app.logger.debug(f'prompt_completions_dict: {prompt_completions_dict}, metric_values: {metric_values}')

        app.logger.info('finish post /_api/stats')
        return render_template('stats_result.html', user_message=user_message, prompt_completions_dict=prompt_completions_dict, metric_values=metric_values)
    except:
        app.logger.error('failed post /_api/stats')
        abort(500)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    app.logger.info('start save settings')
    try:
        payload = request.json
        common_settings = payload['common_settings']
        temperature = payload['temperature']

        app.logger.debug(f'common_settings: {common_settings}, temperature: {temperature}')

        session['common_settings'] = common_settings
        session['temperature'] = temperature

        app.logger.info('finish save settings')
        return jsonify({'status': 'success'})
    except:
        app.logger.error('failed save settings')
        abort(500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)