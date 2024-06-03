# -*- coding: utf-8 -*-
"""
Created on Thu May 30 17:06:39 2024

@author: ASUS
"""

import json
import re

# 定义正则表达式模式
def get_questions_patterns():
    return [
        re.compile(r'(Does.*?)\?', re.DOTALL),
    ]

def find_answer(input_text, answer_start):
    # 查找第一种情况：问题后面直接跟着 Yes|No
    direct_pattern = re.compile(r'\b(Yes|No)\b', re.IGNORECASE)
    direct_match = direct_pattern.search(input_text, answer_start)
    if direct_match:
        return direct_match.group(1)
    
    # 查找第二种情况：'\nOptions:\n- No\n- Yes'
    options_pattern = re.compile(r'\nOptions:\n- (No|Yes)\n- (No|Yes)\s*', re.DOTALL)
    options_match = options_pattern.search(input_text, answer_start)
    if options_match:
        return options_match.group(1)
    
    # 查找第三种情况："No or Yes? (No|Yes)"
    yes_no_pattern = re.compile(r'No or Yes\?\s*(No|Yes)', re.IGNORECASE | re.DOTALL)
    yes_no_match = yes_no_pattern.search(input_text, answer_start)
    if yes_no_match:
        return yes_no_match.group(1)
    
    answer_end = input_text.find('\n', answer_start)
    if answer_end == -1:
        answer_end = len(input_text)
    answer_text = input_text[answer_start:answer_end].strip()
    return answer_text

def clean_text(headline):
    # 去除问题的后缀
    text = re.sub(r'(Q:|Now answer this question:)', '', headline).strip().rstrip('?')
    return text

def clean_headline(headline):
    # 去除标题的前缀和多余引号
    headline = re.sub(r'(Headline:|Answer a question about this headline:|Please answer a question about the following headline:|Read this headline:|")', '', headline).strip().rstrip('?')
    text = re.sub(r'(Q:|Now answer this question:)', '', headline).strip().rstrip('?')
    return text

def extract_headlines_and_questions(input_text):
    headline_pattern = re.compile(r'Headline:\s*"([^"]*)"|Headline:\s*([^\n]+)')
    questions_patterns = get_questions_patterns()
    
    headlines = re.findall(headline_pattern, input_text)
    headlines = [hl[0] if hl[0] else hl[1] for hl in headlines]
    
    all_matches = []
    for pattern in questions_patterns:
        matches = pattern.findall(input_text)
        all_matches.extend(matches)
    
    question_answers = []
    last_index = 0
    for i, match in enumerate(all_matches):
        question_text = match.strip()
        answer_start = input_text.find(question_text, last_index) + len(question_text) + 1
        answer_text = find_answer(input_text, answer_start)
        last_index = answer_start
        if i < len(headlines):
            headline = headlines[i % len(headlines)]
        else:
            # 没有明确的标题时，使用问题前的一行或两行作为标题
            pre_question_text = input_text[:input_text.find(question_text)].strip()
            possible_headlines = pre_question_text.split('\n')[-2:]  # 获取最后两行
            headline = " ".join(possible_headlines).strip()
        headline = clean_headline(headline)
        question_answers.append({"Headline": headline, "Question": clean_text(question_text) + "?", "Answer": answer_text})
    
    return question_answers

# 加载 JSON 文件并处理数据
def process_json_data(json_file_path):
    question_answers_list = []
    
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for item in data:
        input_text = item['input']
        question_answers = extract_headlines_and_questions(input_text)
        
        for qa in question_answers:
            question_answers_list.append({"id": item['id'], "Headline": qa["Headline"], "Question": qa["Question"], "Answer": qa["Answer"]})
    
    return question_answers_list

# 主函数
def main():
    json_file_path = 'test.json'
    question_answers = process_json_data(json_file_path)
    
    # 打印结果或进行其他处理
    for qa in question_answers:
        print(qa)
    
    # 将结果转换为 JSON 格式
    result_json = json.dumps(question_answers, indent=2, ensure_ascii=False)
    with open('question_answers.json', 'w', encoding='utf-8') as file:
        file.write(result_json)

# 运行主函数
if __name__ == '__main__':
    main()