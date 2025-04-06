# Генерируем ответ на основе сообщений
# Используем pipeline как высокоуровневый помощник
from transformers import pipeline

# Используем модель Phi-3-mini-4k-instruct
pipe = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct", trust_remote_code=True)

import json
data = json.load(open('data.json', 'r', encoding='utf-8'))
for el in data:
    messages = [{"role": "user", "content": f'!!!Напиши только Yes/No!!! Yes только если на более чем 75% уверен, что статья относится к вопросу. скажи есть ли решение этого вопроса {"Какие требования к программному обеспечению для работы с порталом?"} в этой статье {data[el]} '}]
    response = pipe(messages, max_new_tokens=5, do_sample=True, temperature=0.7, use_cache=False)
    if 'Yes' in response[0]['generated_text'][-1]['content']:
        print(el, response[0]['generated_text'][-1]['content'])
    else:
        print(el)