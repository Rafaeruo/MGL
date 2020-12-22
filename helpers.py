from flask import session, redirect
from functools import wraps
import requests
import os

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
            f'fields id, name, summary; where id = ({",".join(map(str, game_ids))});'
            )
    return json.loads(byte_array)

def api_game_name_lookup(game_name):#returns json of games or None
    if not game_name:
        return
    byte_array = wrapper.api_request(
            'games',
            f'fields id, name, cover; search "{game_name}"; limit 50; offset 0;'
            )
    return json.loads(byte_array)
