import json
import os
import re
from time import sleep, time

import openai
import tiktoken
import yaml

from shortGPT.config.api_db import ApiKeyManager


def num_tokens_from_messages(texts, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        if isinstance(texts, str):
            texts = [texts]
        score = 0
        for text in texts:
            score += 4 + len(encoding.encode(text))
        return score
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information""")


def extract_biggest_json(string):
    json_regex = r"\{(?:[^{}]|(?R))*\}"
    json_objects = re.findall(json_regex, string)
    if json_objects:
        return max(json_objects, key=len)
    return None


def get_first_number(string):
    pattern = r'\b(0|[1-9]|10)\b'
    match = re.search(pattern, string)
    if match:
        return int(match.group())
    else:
        return None


def load_yaml_file(file_path: str) -> dict:
    """Reads and returns the contents of a YAML file as dictionary"""
    return yaml.safe_load(open_file(file_path))


def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data

from pathlib import Path

def load_local_yaml_prompt(file_path):
    _here = Path(__file__).parent
    _absolute_path = (_here / '..' / file_path).resolve()
    json_template = load_yaml_file(str(_absolute_path))
    return json_template['chat_prompt'], json_template['system_prompt']


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

import g4f
def remove_g4f_finishreason(input_str):
    regex = r"<g4f.*"

    test_str = input_str

    matches = re.finditer(regex, test_str, re.MULTILINE)
    match_end = match_start = 0
    for matchNum, match in enumerate(matches, start=1):
        
        print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        match_start = match.start()
        match_end = match.end()
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            
            print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
    if match_end != match_start != 0:
        test_str = test_str[:match_start]
        print('test_str after edit: ', test_str)

    pattern = r'\$\@\$(v=v\d+\.\d+-rv\d+|v=undefined-rv\d+)\$\@\$(.*?)'
    cleaned_text = re.sub(pattern, '', test_str)


    # regex = r"{ \"(.|\n)*"
    # test_str = cleaned_text
    # matches = re.finditer(regex, test_str, re.MULTILINE)
    # match_end = match_start = 0
    # for matchNum, match in enumerate(matches, start=1):
        
    #     print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    #     match_start = match.start()
    #     match_end = match.end()
    #     for groupNum in range(0, len(match.groups())):
    #         groupNum = groupNum + 1
            
    #         print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
    # if match_end != match_start != 0:
    #     test_str = test_str[match_start:match_end]
    #     print('test_str after edit: ', test_str)
    # return test_str

    return cleaned_text
    # return test_str


def gpt3Turbo_completion(chat_prompt="", system="You are an AI that can give the answer to anything. MAX TOKENS = 400.", temp=0.7, model="gpt-3.5-turbo", max_tokens=1000, remove_nl=True, conversation=None):
    # openai.api_key = ApiKeyManager.get_api_key("OPENAI")
    max_retry = 5
    retry = 0
    while True:
        try:
            if conversation:
                messages = conversation
            else:
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": chat_prompt}
                ]
            # response = openai.chat.completions.create(
            #     model=model,
            #     messages=messages,
            #     max_tokens=max_tokens,
            #     temperature=temp)
            response = g4f.ChatCompletion.create(
                model=g4f.models.blackbox,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temp
            )
            print('response: ', response)
            text = response.strip()
            text = remove_g4f_finishreason(text)
            print('text: ',text)
            if remove_nl:
                text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            if not os.path.exists('.logs/gpt_logs'):
                os.makedirs('.logs/gpt_logs')
            with open('.logs/gpt_logs/%s' % filename, 'w', encoding='utf-8') as outfile:
                outfile.write(f"System prompt: ===\n{system}\n===\n"+f"Chat prompt: ===\n{chat_prompt}\n===\n" + f'RESPONSE:\n====\n{text}\n===\n')
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                raise Exception("GPT3 error: %s" % oops)
            print('Error communicating with OpenAI:', oops)
            sleep(1)