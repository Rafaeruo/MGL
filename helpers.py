from flask import session, redirect
from functools import wraps
import requests
import os
from random import randint

import json
from igdb.wrapper import IGDBWrapper

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
authorization = os.getenv("AUTHORIZATION")

global wrapper
wrapper = IGDBWrapper(client_id, authorization)

def api_request(params):
    global wrapper
    try:
        return wrapper.api_request(*params)
    except requests.HTTPError:
        regen_auth()
        wrapper = IGDBWrapper(client_id, os.getenv("AUTHORIZATION"))
        return wrapper.api_request(*params)

def regen_auth():
    response = requests.post(f"https://id.twitch.tv/oauth2/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}")
    
    if (response.status_code == 200):
        data = response.json()
        os.environ["AUTHORIZATION"] = data["access_token"]
    
  
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
    byte_array = api_request([
            'games',
            f'fields id, name, slug, cover.url; where id = ({",".join(map(str, game_ids))}); limit 500;'
    ])
    return json.loads(byte_array)

def api_game_slug_lookup(game_slug):#returns json of game or None
    if not game_slug:
        return
    byte_array = api_request([
            'games',
            f'fields id, name, summary, slug, cover.url, platforms.name, genres.name, first_release_date, involved_companies.company.name, involved_companies.developer, involved_companies.publisher; where slug = "{game_slug}";'
    ])
    return json.loads(byte_array)

def api_game_name_lookup(game_name, page, limit, limit_display):#returns json of games or None
    if not game_name:
        return
    page = (int(page)-1)*limit_display
    byte_array = api_request([
            'games',
            f'fields name, slug, cover.url; search "{game_name}"; limit ${limit}; offset ${page};'
    ])
    return json.loads(byte_array)

def api_get_random(n):
    ids = []
    for i in range(n):
        ids.append(randint(0, 142043))#some ids don't actually exist but it doesn't matter
    byte_array = api_request([
            'games',
            f'fields id, name, cover.url, slug; where id = ({",".join(map(str, ids))}); limit {n};' 
    ])
    return json.loads(byte_array)
