# Use a pipeline as a high-level helper
import os
from transformers import pipeline

# Настройка пути кэша моделей в директории проекта
os.environ["TRANSFORMERS_CACHE"] = "./model_cache"
os.makedirs("./model_cache", exist_ok=True)

pipe = pipeline("text2text-generation", model="google/flan-t5-large")

# Пример использования модели
question = "Переведи с английского на русский: Hello world!"
result = pipe(question)
print(result[0]["generated_text"])

# Пример с параметрами генерации
result = pipe(
    "Какая столица России?",
    max_length=50,
    temperature=0.7,
    do_sample=True
)
print(result[0]["generated_text"])