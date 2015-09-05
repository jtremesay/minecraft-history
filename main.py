#!/usr/bin/env python3

import arrow
from bottle import Bottle, request, run, template
import requests

try:
    import redis
except ImportError:
    redis = None
else:
    import pickle

app = Bottle()

if redis:
    redis_connetion = redis.StrictRedis(host='localhost', port=6379, db=0)
    try:
        redis_connetion.ping()
    except redis.exceptions.ConnectionError:
        redis_connetion = None
else:
    redis_connetion = None

def memoize(cache_key):
    def decorator(func):
        def inner(key):
            value = None
            if redis_connetion:
                redis_key = 'minecraft_history_{0}_{1}'.format(cache_key, key)
                value = redis_connetion.get(redis_key)
                if value:
                    value = pickle.loads(value)

            if value is None:
                value = func(key)

                if redis_connetion:
                    redis_connetion.set(redis_key, pickle.dumps(value))

            return value

        return inner

    return decorator


@memoize('user_id')
def get_user_id(user_pseudo):
    response = requests.get('https://api.mojang.com/users/profiles/minecraft/{0}'.format(user_pseudo))
    try:
        user_id = response.json()['id']
    except ValueError:
        return None

    return user_id


@memoize('user_names')
def get_user_names(user_id):
    response = requests.get('https://api.mojang.com/user/profiles/{0}/names'.format(user_id))
    try:
        user_names_data = response.json()
    except ValueError:
        return None

    user_names = [{'pseudo': user_name_data['name'], 'date': arrow.get(int(user_name_data['changedToAt']) / 1000).format('YYYY-MM-DD') if 'changedToAt' in user_name_data else 'Original'} for user_name_data in user_names_data]

    return user_names


def get_user_infos(user_pseudo):
    user_id = get_user_id(user_pseudo)
    if not user_id:
        return []

    user_names = get_user_names(user_id)
    if not user_names:
        return []

    return user_names


@app.route('/')
def greet():
    user_pseudo = request.query.user
    if user_pseudo:
        user_infos = get_user_infos(user_pseudo)
    else:
        user_infos = None

    return template('main', user=user_pseudo, user_infos=user_infos)

run(app, server='gunicorn', host='127.0.0.1', port=5000, debug=True)
