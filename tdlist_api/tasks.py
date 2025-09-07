from todolist_dj_aiogram.celery import app


# from .models import Person
# import requests
# import json
# import time

@app.task  # регистриуем таску
def repeat_order_make():
    print('adsdasd')

    # url = 'sdasd'
    # obj = Person.objects.get_or_create(last_name=f'{time.time()}11111111111111111', first_name='1111')
    return "необязательная заглушка"
