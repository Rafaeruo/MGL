import requests

import sqlite3
from sqlite3 import Error

from flask import Flask, render_template, request, session, redirect, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime

from helpers import login_required, api_game_id_lookup, api_game_name_lookup, api_game_slug_lookup, to_json, object_to_json


#set up sqlite3 connction
try:
    db = sqlite3.connect("database.db", check_same_thread=False)
except Error as e:
    print(f"Error: {e}\nShutting down")
    exit()

#set up flask
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "0j5sDEU96HdBN7GD"#secrect key for session encryption
#app.permanent_session_lifetime = timedelta(days=7)#sets how long the session will last

#main code
@app.route("/")
@login_required
def index():
    
    return render_template("index.html", username=session["username"])

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        #ensure the login fields were filled
        if not request.form.get("username"):
            flash("You must provide a username.")
            return render_template("login.html")
        if not request.form.get("password"):
            flash("You must provide a password.")
            return render_template("login.html")
        
        #ensure the user exists and the password matches
        username = request.form.get("username")
        password = request.form.get("password")
        db_cursor = db.cursor()
        db_cursor.execute("SELECT hash, id FROM users WHERE username=?", (username,))

        rows = db_cursor.fetchone()
        if not rows:
            flash("Username provided doesn't exist.")
            return render_template("login.html")

        password_hash = rows[0]
        if not check_password_hash(password_hash, password):
            flash("Password provided is incorrect.")
            return render_template("login.html")
        
        #log user in
        session.permanent = True
        session["user_id"] = rows[1]
        session["username"] = username
        db_cursor.close()
        flash("Logged in")
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out")
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        #ensure the register fields were filled
        if not request.form.get("username"):
            flash("You must provide a username.")
            return render_template("register.html")
        if not request.form.get("password"):
            flash("You must provide a password.")
            return render_template("register.html")
        if not request.form.get("email"):
            flash("You must provide an email.")
            return render_template("register.html")
        if not request.form.get("name"):
            flash("You must provide a name.")
            return render_template("register.html")
        if not request.form.get("confirmation"):
            flash("You must provide a password confirmation.")
            return render_template("register.html")
        #ensure passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Password and password confirmation must match.")
            return render_template("register.html")
        
        #ensure username ins't in use by another user
        username = request.form.get("username")

        if check_user_in_db(db, username):
            flash("The username provided has already been taken.")
            return render_template("register.html")

        #ensure email isn't in use by another user
        email = request.form.get("email")
        db_cursor = db.cursor()
        db_cursor.execute("SELECT email FROM users WHERE email=?", (email,))

        if db_cursor.fetchone():
            flash("The email provided has already been taken.")
            return render_template("register.html")
        db_cursor.close()

        #register user
        password = request.form.get("password")
        name = request.form.get("name")
        db_cursor = db.cursor()
        db_cursor.execute("INSERT INTO users (username, hash, email, name) VALUES(?, ?, ?, ?)", (username, generate_password_hash(password), email, name))
        db.commit()
        db_cursor.close()

        #log user in
        db_cursor = db.cursor()
        db_cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        session["user_id"] = db_cursor.fetchone()[0]
        session["username"] = username
        db_cursor.close()
        flash("Registered and logged in")
        return redirect("/")
    else:
        return render_template("register.html")
    
@app.route("/search")
@login_required
def search():
    game_name = request.args.get("q", None)
    games = api_game_name_lookup(game_name)

    return render_template("search.html", games=games)
    
@app.route("/user/<username>", methods=["POST", "GET"])
@login_required
def profile(username):
    # if request.method == "POST":#when the javascript ajax code requests the game list

    #     user_games_api = get_user_games(db, session["user_id"])#get user game id list from sql database
    #     user_games_api = api_game_id_lookup(user_games_api)#game user games info from api
    #     user_games_info = get_user_games_info(db, session["user_id"])

        
    #     return object_to_json([user_games_api, user_games_info])
    
    
    #check if user exists in the database
    user_id = check_user_in_db(db, username)
    if user_id:
        #check if user is trying to access their own page
        iscurrent = False
        if username == session["username"]:
            iscurrent = True

        user_games = get_user_games(db, user_id)#get user game id list from sql database
        user_games = api_game_id_lookup(user_games)#game user games info from api
        
        info = get_user_games_info(db, user_id)

        return render_template("user.html", username=username, iscurrent=iscurrent, games=user_games, info=info)

    


    #throw 404 if the user doesnt exist
    abort(404)
    
@app.route("/game/<game_slug>", methods=["GET", "POST"])
@login_required
def game(game_slug):
    #check if the game exists in the API db
    game = api_game_slug_lookup(game_slug)
    if not game:
        abort(404)
    game = game[0]
    game_id = game["id"]
    info = check_game_in_user(db, session["user_id"], game_id)

    if "first_release_date" in game.keys():
        game["first_release_date"] = datetime.fromtimestamp(game["first_release_date"]).strftime("%Y-%m-%d")

    #handle post requests
    if request.method == "POST":
        data = to_json(request.get_data())

        action = data["action"]
        if action != "1" and action != "2" and action != "0":
            flash("Invalid action: please don't modify HTML values, smartass")
        elif action == "0":
            if info:
                flash("Invalid action: game already added")
            else:
                edit_user_game(db, session["user_id"], game_id, data["score"], data["status"], action)
        elif action == "1":
            if not info:
                flash("Invalid action: can't update game not added yet")
            else:
                edit_user_game(db, session["user_id"], game_id, data["score"], data["status"], action)
        else:
            if not info:
                flash("Invalid action: can't remove game not added yet")
            else:
                remove_user_game(db, session["user_id"], game_id)
        
        info = check_game_in_user(db, session["user_id"], game_id)
        
        return render_template("game-options.html", info=info)#render the div via ajax so that the js can update the page without reloading

    return render_template("game.html", game=game, info=info)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def check_user_in_db(db, username): #returns user id or False
    db_cursor = db.cursor()
    db_cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    rows = db_cursor.fetchone()

    if rows:
        id = rows[0]
        db_cursor.close()
        return id
    
    db_cursor.close()
    return False

def get_user_games(db, user_id):#returns a list of game ids or None
    db_cursor = db.cursor()
    db_cursor.row_factory = lambda cursor, row: row[0]#stop using tuples for results -> its probably a good idea to do this to all cursors, but that would be super boring
    db_cursor.execute("SELECT game_id FROM userGames WHERE user_id=?", (user_id,))
    rows = db_cursor.fetchall()
    db_cursor.close()
    return rows

def get_user_games_info(db, user_id):#returns list of tuples with the id, score and status
    db_cursor = db.cursor()
    db_cursor.execute("SELECT game_id, score, status FROM userGames WHERE user_id=?", (user_id,))
    rows = db_cursor.fetchall()
    db_cursor.close()
    return rows

def check_game_in_user(db, user_id, game_id):#returns a list with status and score or False
    db_cursor = db.cursor()
    db_cursor.execute("SELECT status, score FROM userGames WHERE game_id=? AND user_id=?", (game_id, user_id,))
    rows = db_cursor.fetchone()
    if rows:
        info = rows
        db_cursor.close()
        return info
    
    db_cursor.close()
    return False

def edit_user_game(db, user_id, game_id, score, status, action):#adds to or updates userGames
    if action == "0":
        db_cursor = db.cursor()
        db_cursor.execute("INSERT INTO userGames (user_id, game_id, score, status) VALUES(?, ?, ?, ?)", (user_id, game_id, score, status,))
        db.commit()
        db_cursor.close()
    elif action == "1":
        print("i started the editing")
        print(score)
        print(status)
        db_cursor = db.cursor()
        db_cursor.execute("UPDATE userGames SET score=?, status=? WHERE user_id=? AND game_id=?", (score, status, user_id, game_id,))
        db.commit()
        print("i finished the editting")
        db_cursor.close()

def remove_user_game(db, user_id, game_id):#remove entry from userGames
    db_cursor = db.cursor()
    db_cursor.execute("DELETE FROM userGames WHERE user_id=? AND game_id=?", (user_id, game_id,))
    db.commit()
    db_cursor.close()
    