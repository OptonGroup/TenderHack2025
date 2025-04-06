import requests
import numpy as np
from collections import defaultdict
import json # Добавляем json для красивого вывода

# --- Функции для расчета метрик ---

def normalize_title(title):
    """Приводит заголовок к нижнему регистру и убирает пробелы по краям."""
    # Добавим проверку на None
    return title.strip().lower() if title else ""

def precision_at_k(predicted_titles, relevant_titles, k):
    """Расчет Precision@k."""
    if not relevant_titles:
        return 0.0 # Нельзя оценить точность, если нет релевантных
    predicted_k = predicted_titles[:k]
    relevant_set = set(relevant_titles)
    hits = sum(1 for title in predicted_k if title in relevant_set)
    return hits / k

def recall_at_k(predicted_titles, relevant_titles, k):
    """Расчет Recall@k."""
    if not relevant_titles:
        return 1.0 # Если релевантных нет, то полнота 100% (нашли все 0)
    predicted_k = predicted_titles[:k]
    relevant_set = set(relevant_titles)
    hits = sum(1 for title in predicted_k if title in relevant_set)
    return hits / len(relevant_titles) if relevant_titles else 1.0 # Деление на 0

def reciprocal_rank(predicted_titles, relevant_titles):
    """Расчет Reciprocal Rank."""
    if not relevant_titles:
        return 0.0
    relevant_set = set(relevant_titles)
    for i, title in enumerate(predicted_titles):
        if title in relevant_set:
            return 1.0 / (i + 1)
    return 0.0

def success_rate_at_k(predicted_titles, relevant_titles, k):
    """Расчет Success Rate@k."""
    if not relevant_titles:
        return 1.0 # Считаем успехом, если не нужно было ничего находить
    predicted_k = predicted_titles[:k]
    relevant_set = set(relevant_titles)
    return 1.0 if any(title in relevant_set for title in predicted_k) else 0.0

# --- Тестовые вопросы (ВАЖНО: Заполните relevant_articles!) ---
questions = [
    {
        'query': "Какие требования к программному обеспечению для работы с порталом?",
        'relevant_articles': [
            "Требования к  программному и техническому обеспечению и уровню подготовки пользователя",
            # Оставляем только подтвержденный релевантный заголовок
        ],
        'weight': 1
    },
    {
        'query': "Как внести новый товар в каталог",
        'relevant_articles': [
            "Какой срок рассмотрения заявок на создание новой позиции СТЕ или внесение изменений в действующую позицию СТЕ?",
            "Как ускорить срок рассмотрения заявки на создание новой позиции СТЕ или внесение изменений в действующую позицию СТЕ?",
            "Кто утверждает новую СТЕ или вносит изменения в действующую позицию СТЕ?"
        ],
        'weight': 1
    },
    {
        'query': "Где получить электронную подпись",
        'relevant_articles': [
             # TODO: Добавьте сюда ТОЧНЫЕ заголовки релевантных статей
        ],
        'weight': 1
    },
    {
        'query': "Какие действия нужно выполнить для обновления прайслиста в электронном магазине?",
        'relevant_articles': [
             "Обновление прайс-листов", # Пример
             "Импорт прайс-листа поставщика" # Пример
        ],
        'weight': 2
    },
    {
        'query': "Как настроить фильтры в едином реестре закупок и сохранить их?",
        'relevant_articles': [
            "Единый реестр закупок" # Пример
        ],
        'weight': 2
    },
    {
        'query': "Как получать нужные уведомления",
        'relevant_articles': [
             # TODO: Добавьте сюда ТОЧНЫЕ заголовки релевантных статей
        ],
        'weight': 2
    },
    {
        'query': "Как использовать симулятор по котировочным сессиям для подготовки к участию в КС?",
        'relevant_articles': [
             # TODO: Возможно, такой статьи нет, оставить пустым
        ],
        'weight': 3
    },
    {
        'query': "Какие шаги необходимо выполнить для создания коммерческого предложения через портал поставщиков?",
        'relevant_articles': [
             # TODO: Добавьте сюда ТОЧНЫЕ заголовки релевантных статей
        ],
        'weight': 3
    },
    {
        'query': "Как осуществляется электронное исполнение контракта, и чем оно отличается от бумажного исполнения?",
        'relevant_articles': [
             # TODO: Добавьте сюда ТОЧНЫЕ заголовки релевантных статей
        ],
        'weight': 3
    },
    {
        'query': "Можно ли создать два упд на один этап",
        'relevant_articles': [
             # TODO: Добавьте сюда ТОЧНЫЕ заголовки релевантных статей
        ],
        'weight': 3
    }
]

# --- Запуск тестов и расчет метрик ---
API_BASE_URL = "http://localhost:7777" # Базовый URL
RECOMMENDATIONS_ENDPOINT = f"{API_BASE_URL}/recommendations" # Новый эндпоинт
TOP_N_RESULTS = 5 # Сколько результатов запрашивать и выводить

results = []
metrics_by_weight = defaultdict(lambda: defaultdict(list))
all_metrics = defaultdict(list)

print("Запуск тестов с запросом детальных рекомендаций...")

for i, q_data in enumerate(questions):
    query_text = q_data['query']
    relevant_titles_norm = {normalize_title(title) for title in q_data['relevant_articles']}
    weight = q_data['weight']

    print(f"\n--- Тест {i+1}/{len(questions)} (Weight: {weight}) ---")
    print(f"Запрос: '{query_text}'")
    print(f"Ожидаемые статьи (норм): {relevant_titles_norm if relevant_titles_norm else '{}'}")

    try:
        params = {"query": query_text, "top_n": TOP_N_RESULTS}
        response = requests.get(RECOMMENDATIONS_ENDPOINT, params=params, timeout=60)
        response.raise_for_status()
        response_data = response.json()

        # Извлекаем предложенные рекомендации
        recommendations = response_data.get("recommendations", [])

        # Извлекаем только заголовки для расчета метрик
        predicted_titles_raw = [rec.get('Заголовок статьи') for rec in recommendations]
        predicted_titles_norm = [normalize_title(title) for title in predicted_titles_raw]

        print("\nПредложенные рекомендации:")
        if recommendations:
            for rank, rec in enumerate(recommendations):
                # Формируем строку с оценками
                scores_str = f"Релевантность={rec.get('релевантность', -1):.4f} " \
                             f"(BM25={rec.get('score_bm25', -1):.4f}, " \
                             f"BERT={rec.get('score_bert', -1):.4f}, " \
                             f"Combined={rec.get('score_combined', -1):.4f}, " \
                             f"Context={rec.get('score_context', -1):.4f})"
                
                # Проверяем, релевантна ли статья согласно нашему списку
                is_relevant = "(+) " if normalize_title(rec.get('Заголовок статьи')) in relevant_titles_norm else "(-) "
                
                print(f"  {rank+1}. {is_relevant}{rec.get('Заголовок статьи', 'N/A')}")
                print(f"     {scores_str}")
                # Можно добавить вывод описания или контекста при необходимости
                # print(f"     Контекст: Тип={rec.get('тип')}, Роль={rec.get('роль')}, Комп={rec.get('компонент')}") 
        else:
            print("  Рекомендации не найдены.")

        # Расчет метрик для этого запроса (используем нормализованные заголовки)
        p1 = precision_at_k(predicted_titles_norm, relevant_titles_norm, 1)
        p3 = precision_at_k(predicted_titles_norm, relevant_titles_norm, 3)
        r3 = recall_at_k(predicted_titles_norm, relevant_titles_norm, 3)
        rr = reciprocal_rank(predicted_titles_norm, relevant_titles_norm)
        s3 = success_rate_at_k(predicted_titles_norm, relevant_titles_norm, 3)

        metrics = {'P@1': p1, 'P@3': p3, 'R@3': r3, 'MRR': rr, 'Success@3': s3}
        
        # --- Дополнительный анализ оценок (без ground truth) ---
        score_analysis = {}
        if recommendations:
            top1_score = recommendations[0].get('релевантность', 0)
            score_analysis['top1_score'] = top1_score
            score_analysis['top1_abs_check'] = top1_score > 0.6 # Порог абсолютной оценки

            if len(recommendations) > 1:
                top2_score = recommendations[1].get('релевантность', 0)
                confidence_gap = top1_score - top2_score
                score_analysis['confidence_gap'] = confidence_gap
                score_analysis['confidence_gap_check'] = confidence_gap > 0.15 # Порог разницы
            else:
                score_analysis['confidence_gap'] = None
                score_analysis['confidence_gap_check'] = None # Не можем проверить
                
            # Проверка баланса BM25/BERT для топ-1
            top1_bm25 = recommendations[0].get('score_bm25', 0)
            top1_bert = recommendations[0].get('score_bert', 0)
            balance_warning = None
            if top1_bm25 > 15 and top1_bert < 0.3: # Примерные пороги
                balance_warning = "High BM25, Low BERT"
            elif top1_bert > 0.8 and top1_bm25 < 5:
                balance_warning = "High BERT, Low BM25"
            score_analysis['balance_warning'] = balance_warning
            
            print(f"\n  Анализ оценок:")
            print(f"    Топ-1 оценка: {top1_score:.4f} (Проверка > 0.6: {score_analysis['top1_abs_check']})")
            if score_analysis['confidence_gap'] is not None:
                print(f"    Разница с Топ-2: {score_analysis['confidence_gap']:.4f} (Проверка > 0.15: {score_analysis['confidence_gap_check']})")
            if balance_warning:
                 print(f"    Предупреждение баланса: {balance_warning}")
        # --------------------------------------------------------
        
        results.append({
            'query': query_text,
            'recommendations': recommendations, # Сохраняем полные данные
            'relevant_norm': relevant_titles_norm,
            'metrics': metrics,
            'score_analysis': score_analysis # Сохраняем анализ оценок
        })

        # Добавляем метрики в статистику
        for m_name, m_value in metrics.items():
             all_metrics[m_name].append(m_value)
             metrics_by_weight[weight][m_name].append(m_value)

        print(f"\n  Метрики для запроса: {metrics}")

    except requests.exceptions.RequestException as e:
        print(f"\n  Ошибка запроса к API: {e}")
        results.append({'query': query_text, 'error': str(e)})
    except Exception as e:
        print(f"\n  Ошибка обработки ответа или расчета метрик: {e}")
        results.append({'query': query_text, 'error': str(e)})

# --- Вывод итоговых результатов ---
print("\n--- Итоговые средние метрики ---")

# Словарь для хранения средних значений
average_metrics = {}

print("\nСредние метрики по всем вопросам:")
if all_metrics:
    for m_name, m_values in all_metrics.items():
        mean_value = np.mean(m_values) if m_values else 0
        average_metrics[m_name] = mean_value # Сохраняем среднее значение
        print(f"  {m_name}: {mean_value:.4f}")
else:
    print("  Нет данных для расчета средних метрик.")

# --- Расчет и вывод общей оценки ---
overall_score = 0
if average_metrics:
    # Берем среднее по всем рассчитанным средним метрикам (P@1, P@3, R@3, MRR, Success@3)
    metrics_for_average = [average_metrics.get(m, 0) for m in ['P@1', 'P@3', 'R@3', 'MRR', 'Success@3']]
    overall_score = np.mean(metrics_for_average) * 100
    print(f"\n--- Общая оценка успешности модели (0-100): {overall_score:.1f} ---")
else:
    print("\n--- Невозможно рассчитать общую оценку (нет метрик) ---")
# ------------------------------------

print("\nСредние метрики по сложности (weight):")
for weight in sorted(metrics_by_weight.keys()):
    print(f"  Сложность {weight}:")
    weight_metrics = metrics_by_weight[weight]
    if weight_metrics:
        for m_name, m_values in weight_metrics.items():
             mean_value = np.mean(m_values) if m_values else 0
             print(f"    {m_name}: {mean_value:.4f}")
    else:
         print("    Нет данных для этой сложности.")

# Можно добавить вывод детальных результатов по каждому запросу, если нужно
# print("Детальные результаты:")
# for res in results:
#    print(res)
