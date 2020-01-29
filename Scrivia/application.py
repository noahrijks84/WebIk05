"""
****************************************************************************
 * SCRIVIA - DRAWING AND TRIVIA GAME
 * applications.py
 *
 * Webprogrammeren en Databases IK
 * Sava Arbutina, Noah Milidragović, Rogier Wesseling, Nick Duijm
 *
 * The controller for our game SCRIVIA, where you can draw and answer trivia.
****************************************************************************
"""

import os
from cs50 import SQL
import time, random
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_socketio import SocketIO, emit, send, join_room, leave_room, rooms
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import re
import logging
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

# Removing the user from the lobby when closing/reloading the tab
@app.route("/leaverequest")
@login_required
def on_pageleave():
    username = session["username"]
    if username in current_users:
        room = current_users[username][0]
        current_users[username][0] = None
        current_users[username][1] = 0
        current_users[username][2] = None
        current_users[username][3] = 0
        current_users[username][4] = None

        message = username + " has left the game"
        lobby_players = [k for k,v in current_users.items() if v[0] == room]
        socketio.emit("playerupdate", len(lobby_players),  broadcast=True, room=room)
        socketio.emit('user message', message, broadcast=True, room=room)
    return jsonify(True)

# Removing the user from the lobby when navigating to the lobby page
@socketio.on('leaverequest')
@login_required
def on_leave_request():
    username = session["username"]
    if username in current_users:
        current_users[username][0] = None
        current_users[username][1] = 0
        current_users[username][2] = None
        current_users[username][3] = 0
        current_users[username][4] = None

# Adding the playerr to the chosen lobby
@socketio.on('lobbyrequest')
@login_required
def on_lobby_request(lobby, category, gamemode):
    username = session["username"]
    hearts = 0
    if gamemode == 'timeattack':
        lobby = username
    
    join_room(lobby)
    current_users[username] = [lobby, 0, category, hearts, gamemode]
    print(current_users[username])
    

# readding the user to the chosen lobby when entering the game page
@socketio.on('joinrequest')
@login_required
def on_join_request():
    username = session["username"]
    if username in current_users:
        lobby = current_users[username][0]
        if lobby != None:
            join_room(lobby)
            room = lobby
            lobby_players = [k for k,v in current_users.items() if v[0] == room]
            message = username + " has joined the game"
            emit("playerupdate", len(lobby_players),  broadcast=True, room=room)
            emit('user message', message, broadcast=True, room=room)
            print(current_users[username])
        else:
            emit("nolobby")
    else:
        emit("nolobby")

# Requesting a question from the api
def get_questions(category, type):
    import requests
    url = 'https://opentdb.com/api.php'
    if type == 'timeattack':
        parameters = {'amount': '1', 'type': 'multiple', 'category': category}
    elif type == 'regular':
        parameters = {'amount': '1', 'type': 'multiple', 'category': category, 'difficulty': 'easy'}
    response = requests.get(url, params=parameters)
    response.raise_for_status()
    json_response = response.json()['results']
    return json_response
    
# Making the question usable in terms of format
def call_question(cate, diff, questionset):
    question = get_questions(cate, diff)[0]
    intlist =  [int(i) for i in question['correct_answer'].split() if i.isdigit()]
    if len(intlist) >= 1 or question['correct_answer'] in questionset:
        return call_question(cate, diff, questionset)
    else:
        return question

# Running a game for players inside the specific lobby
@socketio.on('startgame')
@login_required
def game_start(category):
    username = session["username"]
    room = current_users[username][0]
    lobby_players = [k for k,v in current_users.items() if v[0] == room]
    questionset = set()
    catlook = category 

    for player in lobby_players:
        if player in current_users:
            if current_users[player][0] == room:
                current_users[player][1] = 0
                current_users[player][2] = catlook

    # iterating thru the players in the lobby
    for host in lobby_players:
        category_list = ['any','animals', 'video_games', 'celebrities', 'comics', 'general_knowledge',
                            '27', '15', '26', '29', '9']

        for cat in range(int(len(category_list) / 2.0)):
            if category_list[cat] == catlook:
                category = category_list[cat + 5]

        triv = call_question(category, 'regular', questionset)
        correct = triv['correct_answer']
        question = triv["question"]
        answers = triv["incorrect_answers"]
        answers.append(correct)
        random.shuffle(answers)

        current_hosts[room] = host
        correct_answers[room] = correct

        questionset.add(correct)

        # formatting data to display with the host player
        hostdata = question + " answer: " + correct

        # letting javascript run the drawing fase at the client
        emit('fase1', (host, hostdata), broadcast=True, room=room)
        time.sleep(10)

        # letting javascript run the guessing fase at the client
        emit('fase2', (host, answers, question, correct), broadcast=True, room=room)
        time.sleep(10)

    # letting javascript run the endfase of the game finishing everything up
    emit('endfase', broadcast=True, room=room)
    # iterating thru players left in te lobby
    for player in lobby_players:
        if player in current_users:
            if current_users[player][0] == room:
                # clearing all the player data
                username = player
                points = current_users[player][1]

                # emitting a request to register the user points
                emit("pointsregister", (username, points, catlook))
                current_users[player][2] = None
    time.sleep(10)


@socketio.on('startTimeAttack')
@login_required
def TimeAttack_start():
    username = session["username"]
    room = username
    current_users[username][3] = 3

    questionset = set()
    timeout = 90
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:

        if current_users[username][3] <= 0:
            break
        lives = current_users[username][3]
        catlook = current_users[username][2]

        category_list = ['animals', 'video_games', 'celebrities', 'comics', 'general_knowledge',
                            '27', '15', '26', '29', '9']
        for cat in range(int(len(category_list) / 2.0)):
            if category_list[cat] == catlook:
                category = category_list[cat + 5]

        triv = call_question(category, 'timeattack', questionset)

        correct = triv['correct_answer']
        question = triv["question"]
        answers = triv["incorrect_answers"]

        answers.append(correct)
        random.shuffle(answers)
        correct_answers[room] = correct
        
        questionset.add(correct)

        emit('newround', (answers, question, correct, lives), broadcast=True, room=room)
        time.sleep(7)
        emit("timeup")
        time.sleep(3)

    emit('endfase', broadcast=True)
    if username in current_users:
        if current_users[username][0] == room:
            points = current_users[username][1]
            category = current_users[username][2]

            emit("pointsregister", (username, points, category))
            current_users[username][1] = 0
    time.sleep(10)

@socketio.on("pointsrequest")
@login_required
def on_requestpoints():
    username = session["username"]
    points = current_users[username][1]
    emit("pointsreturn", points)


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

    print(answer)
    print(correct_answers[lobby])


    if current_users[username][4] == 'timeattack':
        if correct_answers[lobby] == answer:
            current_users[username][1] += 3
        else:
            current_users[username][3] -= 1
    elif current_users[username][4] == 'classic':
        host = current_hosts[lobby]
        if correct_answers[lobby] == answer:
            current_users[username][1] += 3
            current_users[host][1] += 1


# emitting the picture drawn by the host
@socketio.on('picture')
def handle_user_picture(message):
    username = session["username"]
    room = current_users[username][0]
    emit('picture', message, broadcast=True, room=room)

# emitting user chat messages to other players in the room
@socketio.on('chat message')
@login_required
def handle_user_chat(message):
    username = session["username"]
    message = username + ": " + message
    room = current_users[username][0]
    emit('user message', message, broadcast=True, room=room)

# returning a requested player username
@app.route("/getusername", methods=["GET"])
@login_required
def username():
    return session["username"]


@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


@app.route("/landing", methods=["GET"])
def landing():
    return render_template("landing.html")


@app.route("/game", methods=["GET"])
@login_required
def game():
    return render_template("game.html")


@app.route("/timeattack", methods=["GET"])
@login_required
def timeattack():
    return render_template("timeattack.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

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

@app.route("/leaderboards_classic", methods=["GET", "POST"])
@login_required
def leaderboards_classic():
    """Show leaderboards of top 10 ranked players for the Classic game mode, can also filter by categories"""

    # List of the categories to send to HTML
    categories = ["Animals", "Video Games", "Celebrities", "Comics", "General Knowledge"]

    # Retrieves the the sum of the points of all the categories for the Classic game mode
    total_points = scrivdb.execute("SELECT *, SUM(animals + video_games + celebrities + comics + general_knowledge), username FROM statistics WHERE points > 0  GROUP BY username ORDER BY SUM(animals + video_games + celebrities + comics + general_knowledge) DESC LIMIT 10")

    # Retrieves the points per category for the Classic game mode
    animals_points = scrivdb.execute("SELECT animals, username FROM statistics WHERE animals > 0 GROUP BY username ORDER BY animals DESC LIMIT 10")
    video_games_points = scrivdb.execute("SELECT video_games, username FROM statistics WHERE video_games > 0 GROUP BY username ORDER BY video_games DESC LIMIT 10")
    celebrities_points = scrivdb.execute("SELECT celebrities, username FROM statistics WHERE celebrities > 0 GROUP BY username ORDER BY celebrities DESC LIMIT 10")
    comics_points = scrivdb.execute("SELECT comics, username FROM statistics WHERE comics > 0 GROUP BY username ORDER BY comics DESC LIMIT 10")
    general_knowledge_points = scrivdb.execute("SELECT general_knowledge, username FROM statistics WHERE general_knowledge > 0 GROUP BY username ORDER BY general_knowledge DESC LIMIT 10")

    return render_template("leaderboards_classic.html", total_points=total_points, categories=categories, animals_points=animals_points, video_games_points=video_games_points,
    celebrities_points=celebrities_points, comics_points=comics_points, general_knowledge_points=general_knowledge_points)

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    # password = request.form.get("password")
    # new_password = request.form.get("new_password")
    # new_confirm = request.form.get("new_confirm")

    if request.method == "POST":
        # Make sure password was acknowledged
        if not request.form.get("password"):
            return apology("must provide old password", 400)

        # Make sure new password was acknowledged
        elif not request.form.get("new_password"):
            return apology("must provide new password", 400)

        # New password must match the regex pattern
        elif not re.search(r"^(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", request.form.get("new_password")):
            return apology("invalid password format", 400)

        # New password must be at least 7 characters long
        elif len(request.form.get("new_password")) < 7:
            return apology("new password must be at least 7 characters long", 400)

        # Make sure confirmation was acknowledged
        elif not request.form.get("new_confirm"):
            return apology("must provide confirmation", 400)

        # Make sure the new password is different to the old one
        elif request.form.get("new_password") == request.form.get("password"):
            return apology("must provide different password", 400)

        # If passwords do not match, show error
        elif not request.form.get("new_confirm") == request.form.get("new_password"):
            return apology("passwords must match", 400)

        # Make sure password satisfies
        password_hash = scrivdb.execute("SELECT hash FROM users WHERE id = :user", user=session["user_id"])
        if not check_password_hash(password_hash[0]["hash"], request.form.get("password")):
            return apology("wrong password", 400)

        # Replace the old password
        scrivdb.execute("UPDATE users SET hash= :hash WHERE id= :user", hash=generate_password_hash(
            request.form.get("new_password"), method='pbkdf2:sha256', salt_length=8), user=session["user_id"])

        return redirect("/")
    else:
        return render_template("change_password.html")

@app.route("/leaderboards_timeattack", methods=["GET", "POST"])
@login_required
def leaderboards_timeattack():
    """Show leaderboards of top 10 players for the TimeAttack! game mode, can filter by category"""

    # List of the categories to send to HTML
    categories = ["Animals", "Video Games", "Celebrities", "Comics", "General Knowledge"]

    # Show the the sum of the points of all the categories for the TimeAttack! game mode
    total_points = scrivdb.execute("SELECT *, SUM(animals + video_games + celebrities + comics + general_knowledge), username FROM timeattack WHERE points > 0 GROUP BY username ORDER BY SUM(animals + video_games + celebrities + comics + general_knowledge) DESC LIMIT 10")

    # Show the points per category for the TimeAttack! game mode
    animals_points = scrivdb.execute("SELECT animals, username FROM timeattack WHERE animals > 0 GROUP BY username ORDER BY animals DESC LIMIT 10")
    video_games_points = scrivdb.execute("SELECT video_games, username FROM timeattack WHERE video_games > 0 GROUP BY username ORDER BY video_games DESC LIMIT 10")
    celebrities_points = scrivdb.execute("SELECT celebrities, username FROM timeattack WHERE celebrities > 0 GROUP BY username ORDER BY celebrities DESC LIMIT 10")
    comics_points = scrivdb.execute("SELECT comics, username FROM timeattack WHERE comics > 0 GROUP BY username ORDER BY comics DESC LIMIT 10")
    general_knowledge_points = scrivdb.execute("SELECT general_knowledge, username FROM timeattack WHERE general_knowledge > 0 GROUP BY username ORDER BY general_knowledge DESC LIMIT 10")

    return render_template("leaderboards_timeattack.html", total_points=total_points, categories=categories, animals_points=animals_points, video_games_points=video_games_points, celebrities_points=celebrities_points, 
    comics_points=comics_points, general_knowledge_points=general_knowledge_points)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

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
        scrivdb.execute("INSERT INTO statistics (username) VALUES(:username)", username=request.form.get("username"))
        scrivdb.execute("INSERT INTO timeattack (username) VALUES(:username)", username=request.form.get("username"))

    # Rerun the login code to send the user to the index page after registration
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
        return render_template("register.html")


@app.route("/profilepage", methods=["GET"])
@login_required
def profilepage():
    date_joined = scrivdb.execute("SELECT date_joined FROM users WHERE username = :username",
            username=session["username"])

    # Retrieves the user's personal statistics
    personal_statistics_classic = scrivdb.execute("SELECT * FROM statistics WHERE username = :username",
            username=session["username"])
    personal_statistics_timeattack = scrivdb.execute("SELECT * FROM timeattack WHERE username = :username",
            username=session["username"])

    return render_template("profilepage.html", username=session["username"], date_joined=date_joined[0]['date_joined'], personal_statistics_classic=personal_statistics_classic,
    personal_statistics_timeattack=personal_statistics_timeattack)


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
