import requests

res_1 = 'заявка'
res_2 = 'звявка'

try:
    if requests.get(f'http://localhost:7777/query?query={res_1}').json()['sources'][0] == requests.get(f'http://localhost:7777/query?query={res_2}').json()['sources'][0]:
        print('OK')
    else:
        print('Error')
except Exception as e:
    print(f'Error: {e}')

