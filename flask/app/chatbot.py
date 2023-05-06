import os
import time
import configparser
from concurrent.futures import ThreadPoolExecutor

import openai
import tiktoken

import utils

config = configparser.ConfigParser()
config.read('./config.ini')

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

class Chatbot:
    def __init__(self):
        self.model_name = config.get('chatbot', 'model_name')
        self.enc = self.get_encoding(self.model_name)
        self.stats_run = config.getint('chatbot', 'stats_run')

    def get_response(self, elem_id, prompt_suffix, user_message, common_settings, temperature, with_stats=False):
        start = time.time()

        if common_settings != '':
            prompt = f'{common_settings}\n\n{prompt_suffix}'
        else:
            prompt = prompt_suffix
            
        messages = [{'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': user_message}]

        result = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature
        )

        completion = result.choices[0]['message']['content']

        end = time.time()
        elapsed_time = end - start

        if with_stats:
            num_chars = len(completion)
            num_tokens = self.count_tokens(completion)
            
            return {'elem_id': elem_id, 'prompt': prompt, 'user_message': user_message, 'completion': completion, 'num_chars': num_chars, 'num_tokens': num_tokens, 'elapsed_time': elapsed_time}
        else:
            return {'elem_id': elem_id, 'prompt': prompt, 'user_message': user_message, 'completion': completion}

    def get_multiple_response(self, id2prompt, user_message, common_settings, temperature):
        with ThreadPoolExecutor(max_workers=4) as executor:
            features = [executor.submit(self.get_response, elem_id, prompt_suffix, user_message, common_settings, temperature, False) for elem_id, prompt_suffix in id2prompt.items()]
            res = [feat.result() for feat in features]
        return res
    
    def get_stats(self, id2prompt, user_message, common_settings, temperature):
        with ThreadPoolExecutor(max_workers=4) as executor:
            features = [executor.submit(self.get_response, elem_id, prompt_suffix, user_message, common_settings, temperature, True) for elem_id, prompt_suffix in list(id2prompt.items()) * self.stats_run]
            res = [feat.result() for feat in features]

            prompt_completions_dict, metric_values = utils.parse_result(res)

        return user_message, prompt_completions_dict, metric_values
    
    def count_tokens(self, message):
        return len(self.enc.encode(message))
    
    def get_encoding(self, model_name):
        default_tokenizer = 'cl100k_base'
        try:
            enc = tiktoken.encoding_for_model(model_name)
        except:
            enc = tiktoken.get_encoding(default_tokenizer)
        return enc