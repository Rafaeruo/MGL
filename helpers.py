from flask import session, redirect
from functools import wraps
import requests
import os
from random import randint

import json
from igdb.wrapper import IGDBWrapper
wrapper = IGDBWrapper(os.getenv("CLIENT_ID"), os.getenv("AUTHORIZATION"))

#https://flask.palletsprojects.com/en/1.0.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def api_game_id_lookup(game_ids):#returns json of game or None
    if not game_ids:
        return
    byte_array = wrapper.api_request(
            'games',
            f'fields id, name, slug, cover.url; where id = ({",".join(map(str, game_ids))}); limit 500;'
            )
    return json.loads(byte_array)

def api_game_slug_lookup(game_slug):#returns json of game or None
    if not game_slug:
        return
    byte_array = wrapper.api_request(
            'games',
            f'fields id, name, summary, slug, cover.url, platforms.name, genres.name, first_release_date, involved_companies.company.name, involved_companies.developer, involved_companies.publisher; where slug = "{game_slug}";'
            )
    return json.loads(byte_array)

def api_game_name_lookup(game_name, page, limit, limit_display):#returns json of games or None
    if not game_name:
        return
    page = (int(page)-1)*limit_display
    byte_array = wrapper.api_request(
            'games',
            f'fields name, slug, cover.url; search "{game_name}"; limit ${limit}; offset ${page};'
            )
    return json.loads(byte_array)

def api_get_random(n):
    ids = []
    for i in range(n):
        ids.append(randint(0, 142043))#some ids don't actually exist but it doesn't matter
    byte_array = wrapper.api_request(
            'games',
            f'fields id, name, cover.url, slug; where id = ({",".join(map(str, ids))}); limit {n};' 
            )
    return json.loads(byte_array)
