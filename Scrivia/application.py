import os
from cs50 import SQL
import time, random
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_socketio import SocketIO, emit, send, join_room, leave_room, rooms
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
import json
import re
import logging


# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, manage_session=False)

# show prints
logging.basicConfig(level=logging.DEBUG)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure CS50 Library to use SQLite database
trivdb = SQL("sqlite:///trivdb.db")
scrivdb = SQL("sqlite:///scrivia.db")

current_users = {}
correct_answers = {}
current_hosts = {}

@app.route("/leaverequest")
@login_required
def on_pageleave():
    username = session["username"]
    if username in current_users:
        current_users[username][0] = None
        current_users[username][1] = 0
        current_users[username][2] = None
    return jsonify(True)

@socketio.on('leaverequest')
@login_required
def on_leave_request():
    username = session["username"]
    if username in current_users:
        current_users[username][0] = None
        current_users[username][1] = 0
        current_users[username][2] = None

@socketio.on('lobbyrequest')
@login_required
def on_lobby_request(lobby, category):
    username = session["username"]
    print(category)
    join_room(lobby)
    current_users[username] = [lobby, 0, category]

@socketio.on('joinrequest')
@login_required
def on_join_request():
    print(current_users)
    username = session["username"]
    if username in current_users:
        lobby = current_users[username][0]
        if lobby != None:
            join_room(lobby)
        else:
            return redirect("/")
    else:
        return redirect("/")


def get_questions(amount, category):
    import requests
    url = 'https://opentdb.com/api.php'
    parameters = {'amount': amount, 'type': 'multiple', 'category': category, 'difficulty' : 'easy'}
    response = requests.get(url, params=parameters)
    response.raise_for_status()
    json_response = response.json()['results']
    return json_response
    

def call_question_gk():
    question = get_questions(1, 27)[0]
    intlist =  [int(i) for i in question['correct_answer'].split() if i.isdigit()]
    print(intlist)
    if len(intlist) >= 1:
        return call_question_gk()
    else:
        return question

@socketio.on('startgame')
@login_required
def game_start():
    username = session["username"]
    room = current_users[username][0]
    lobby_players = [k for k,v in current_users.items() if v[0] == room]
    print(lobby_players)

    for host in lobby_players:
        triv = call_question_gk()
        correct = triv['correct_answer']
        question = triv["question"]
        answers = triv["incorrect_answer"]
        answers.append(correct)
        random.shuffle(answers)

        current_hosts[room] = host
        correct_answers[room] = correct

        hostdata = question + " answer: " + correct

        emit('fase1', (host, hostdata), broadcast=True, room=room)
        time.sleep(10)

        emit('fase2', (host, answers, question, correct), broadcast=True, room=room)
        time.sleep(10)

    emit('endfase', broadcast=True)
    for player in lobby_players:
        if player in current_users:
            if current_users[player][0] == room:
                username = player
                points = current_users[player][1]
                category = current_users[player][2]

                emit("pointsregister", (username, points, category))
                # scrivdb.execute("UPDATE statistics SET points = points + :points WHERE username = :username",
                #         points=points,
                #         username=username)
                # scrivdb.execute("UPDATE statistics SET :category = :category + :points WHERE username = :username",
                #         points=points,
                #         username=username,
                #         category=category)

        print(player + ": " + str(current_users[player][1]))
        current_users[player][1] = 0
    time.sleep(10)

@app.route("/registerpoints")
@login_required
def on_registerpoints():
    round_data = request.args.get("round_data")
    split_data = round_data.split(',')
    username = split_data[0]
    points = split_data[1]
    category = split_data[2]

    scrivdb.execute("UPDATE statistics SET points = points + :points WHERE username = :username",
            points=points,
            username=username)
    scrivdb.execute("UPDATE statistics SET :category = :category + :points WHERE username = :username",
            points=points,
            username=username,
            category=category)

    return jsonify(True)
    


@socketio.on('answer')
@login_required
def on_answer(answer):
    username = session["username"]
    lobby = current_users[username][0]
    if correct_answers[lobby] == answer:
        current_users[username][1] += 3
        host = current_hosts[lobby]
        current_users[host][1] += 1

@socketio.on('picture')
def handle_user_picture(message):
    emit('picture', message, broadcast=True)


@socketio.on('chat message')
@login_required
def handle_user_chat(message):
    username = session["username"]
    message = username + ": " + message
    room = current_users[username][0]
    emit('user message', message, broadcast=True, room=room)

@app.route("/getusername", methods=["GET"])
@login_required
def username():
    return session["username"]

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")

@app.route("/game", methods=["GET"])
@login_required
def game():
    return render_template("game.html")


@app.route("/check", methods=["GET"])
def check():
    
    # retrieving username
    username = request.args.get("username").strip()
    
    # retrieving existing usernames
    answer = scrivdb.execute("SELECT * FROM users WHERE username = :username", username = username)
    
    # checking if username existed
    data = not len(answer) > 0

    return jsonify(data)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = scrivdb.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/leaderboards", methods=["GET", "POST"])
@login_required
def leaderboards():
    # list of the categories to send to HTML
    categories = ["Animals", "Video Games", "Celebrities", "Comics", "General Knowledge"]

    # show the the sum of the points of all the categories
    total_points = scrivdb.execute("SELECT *, SUM(animals + video_games + celebrities + comics + general_knowledge), username FROM statistics GROUP BY username ORDER BY SUM(animals + video_games + celebrities + comics + general_knowledge) DESC")

    # show the points per category
    animals_points = scrivdb.execute("SELECT animals, username FROM statistics GROUP BY username ORDER BY animals DESC")
    video_games_points = scrivdb.execute("SELECT video_games, username FROM statistics GROUP BY username ORDER BY video_games DESC")
    celebrities_points = scrivdb.execute("SELECT celebrities, username FROM statistics GROUP BY username ORDER BY celebrities DESC")
    comics_points = scrivdb.execute("SELECT comics, username FROM statistics GROUP BY username ORDER BY comics DESC")
    general_knowledge_points = scrivdb.execute("SELECT general_knowledge, username FROM statistics GROUP BY username ORDER BY general_knowledge DESC")

    return render_template("leaderboards.html", total_points=total_points, categories=categories, animals_points=animals_points, video_games_points=video_games_points,
    celebrities_points=celebrities_points, comics_points=comics_points, general_knowledge_points=general_knowledge_points)



@app.route("/register", methods=["GET", "POST"])
def register():
    # """Register user"""
    # # Forget any user_id
    # session.clear()

    # # User reached route via POST (as by submitting a form via POST)
    # if request.method == "POST":

    #     # Ask user to input username
    #     if not request.form.get("username"):
    #         return apology("must input username", 400)

    #     # Ask user to input password
    #     elif not request.form.get("password"):
    #         return apology("must input password", 400)

    #     # Password must be at least 7 characters long
    #     if len(request.form.get("password")) < 7:
    #         return apology("password must be at least 7 characters long", 400)

    #     # If passwords do not match, show error
    #     elif not request.form.get("confirmation") == request.form.get("password"):
    #         return apology("passwords must match", 400)

    #     # Register username and hashed password
    #     registration = scrivdb.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
    #     scrivdb.execute("INSERT INTO statistics (username) VALUES(:username)", username=request.form.get("username"))

        
    #     # If username already exists, show error
    #     if not registration:
    #         return apology("username already exists, choose another", 400)

    #     # Get the registered users id
    #     user_id = scrivdb.execute("SELECT id FROM users WHERE username = :username", username=request.form.get("username"))

    #     # Remember that the user has logged in
    #     session["user_id"] = user_id[0]["id"]

    #     # Redirect user to home page
    #     return redirect("/login")

    # # User reached route via GET (as by clicking a link or via redirect)
    # else:
    #     return render_template("register.html")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # if username contains whitespace at the beginning or end
        elif re.search(r"^\s|\s$", request.form.get("username")):
            return apology("invalid username format", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        
        # Password must match the regex pattern
        elif not re.search(r"^(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", request.form.get("password")):
            return apology("invalid password format", 400)

        # Password must be at least 7 characters long
        elif len(request.form.get("password")) < 7:
            return apology("password must be at least 7 characters long", 400)

        # If passwords do not match, show error
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("passwords must match", 400)
       
        # Check if username is taken
        answer = scrivdb.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))
        if len(answer) > 0:
            return apology("username was already taken", 403)

        # Query: insert values in database
        scrivdb.execute("INSERT INTO users (username, hash) VALUES (:username, :password)", username = request.form.get("username"), password=generate_password_hash(request.form.get("password")))
        
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=3000)
