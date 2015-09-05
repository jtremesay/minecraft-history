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

USE_REDIS = True
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY_PREFIX = 'minecraft_history'

app = Bottle()


def get_redis_connection(host, port, db):
    connection = redis.StrictRedis(host=host, port=port, db=db)
    try:
        connection.ping()
    except redis.exceptions.ConnectionError:
        connection = None


def memoize(cache_key, duration=None):
    def decorator(func):
        def inner(key):
            value = None
            if redis_connection:
                redis_key = 'minecraft_history_{0}_{1}'.format(cache_key, key)
                value = redis_connection.get(redis_key)
                if value:
                    value = pickle.loads(value)

            if value is None:
                value = func(key)

                if redis_connection:
                    redis_connection.set(redis_key, pickle.dumps(value))
                    if duration:
                        redis_connection.expires(redis_key, duration)

            return value

        return inner

    return decorator


if redis and USE_REDIS:
    redis_connection = get_redis_connection(REDIS_HOST, REDIS_PORT, REDIS_DB)
else:
    redis_connection = None


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
