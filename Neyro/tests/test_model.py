import requests

questions = [
    {
        'query': "Какие требования к программному обеспечению для работы с порталом?",
        'relevant_articles': [
            "Требования к  программному и техническому обеспечению и уровню подготовки пользователя",
            
        ],
        'weight': 1
    },
    {
        'query': "Как внести новый товар в каталог",
        'relevant_articles': [
            
        ],
        'weight': 1
    },
    {
        'query': "Где получить электронную подпись",
        'relevant_articles': [
            
        ],
        'weight': 1
    },


    {
        'query': "Какие действия нужно выполнить для обновления прайслиста в электронном магазине?",
        'relevant_articles': [
            
        ],
        'weight': 2
    },
    {
        'query': "Как настроить фильтры в едином реестре закупок и сохранить их?",
        'relevant_articles': [
            
        ],
        'weight': 2
    },
    {
        'query': "Как получать нужные уведомления",
        'relevant_articles': [
            
        ],
        'weight': 2
    },


    {
        'query': "Как использовать симулятор по котировочным сессиям для подготовки к участию в КС?",
        'relevant_articles': [
            
        ],
        'weight': 3
    },
    {
        'query': "Какие шаги необходимо выполнить для создания коммерческого предложения через портал поставщиков?",
        'relevant_articles': [
            
        ],
        'weight': 3
    },
    {
        'query': "Как осуществляется электронное исполнение контракта, и чем оно отличается от бумажного исполнения?",
        'relevant_articles': [
            
        ],
        'weight': 3
    },
    {
        'query': "Можно ли создать два упд на один этап",
        'relevant_articles': [
            
        ],
        'weight': 3
    }

    
]

for question in questions:
    response = requests.post(
        "http://localhost:7777/query",
        json={"query": question},
    )
    print(response.json())
