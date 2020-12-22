import requests

import sqlite3
from sqlite3 import Error

from flask import Flask, render_template, request, session, redirect, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

from helpers import login_required, api_game_id_lookup, api_game_name_lookup


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
    
@app.route("/user/<username>")
@login_required
def profile(username):
    #check if user exists in the database
    user_id = check_user_in_db(db, username)
    if user_id:
        #check if user is trying to access their own page
        iscurrent = False
        if username == session["username"]:
            iscurrent = True
        
        user_games = get_user_games(db, user_id)#get user game id list from sql database
        user_games = api_game_id_lookup(user_games)#game user games info from api

        return render_template("user.html", username=username, iscurrent=iscurrent, games=user_games)


    #throw 404 if the user doesnt exist
    abort(404)
    
@app.route("/game/<game_id>")
@login_required
def game(game_id):
    game = api_game_id_lookup([game_id])
    if not game:
        abort(404)

    game = game[0]
    return render_template("game.html", game=game)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def check_user_in_db(db, username): #if exists, returns user id. else, returns False
    db_cursor = db.cursor()
    db_cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    rows = db_cursor.fetchone()

    if rows:
        id = rows[0]
        db_cursor.close()
        return id
    
    db_cursor.close()
    return False

def get_user_games(db, user_id):
    db_cursor = db.cursor()
    db_cursor.execute("SELECT game_id FROM userGames WHERE user_id=?", (user_id,))
    rows = db_cursor.fetchall()
    db_cursor.close()
    return rows