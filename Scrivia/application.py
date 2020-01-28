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
import json

# configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, manage_session=False)

# ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# configure CS50 Library to use SQLite database
trivdb = SQL("sqlite:///trivdb.db")
scrivdb = SQL("sqlite:///scrivia.db")

current_users = {}
correct_answers = {}
current_hosts = {}

# removing the user from the lobby when closing/reloading the tab
@app.route("/leaverequest")
@login_required
def on_pageleave():
    username = session["username"]
    if username in current_users:
        print(username)
        room = current_users[username][0]
        current_users[username][0] = None
        current_users[username][1] = 0
        current_users[username][2] = None
        current_users[username][3] = None
        current_users[username][4] = 0

        message = username + " has left the game"
        lobby_players = [k for k,v in current_users.items() if v[0] == room]
        socketio.emit("playerupdate", len(lobby_players),  broadcast=True, room=room)
        socketio.emit('user message', message, broadcast=True, room=room)
    return jsonify(True)

# removing the user from the lobby when navigating to the lobby page
@socketio.on('leaverequest')
@login_required
def on_leave_request():
    username = session["username"]
    if username in current_users:
        current_users[username][0] = None
        current_users[username][1] = 0
        current_users[username][2] = None
        current_users[username][3] = None
        current_users[username][4] = 0

# adding the playerr to the chosen lobby
@socketio.on('lobbyrequest')
@login_required
def on_lobby_request(lobby, category, gamemode):
    username = session["username"]
    join_room(lobby)
    hearts = 0
    current_users[username] = [lobby, 0, category, gamemode, hearts]

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
        else:
            emit("nolobby")
    else:
        emit("nolobby")
        

# requesting a question from the api
def get_questions(amount, category):
    import requests
    url = 'https://opentdb.com/api.php'
    parameters = {'amount': amount, 'type': 'multiple', 'category': category, 'difficulty' : 'easy'}
    response = requests.get(url, params=parameters)
    response.raise_for_status()
    json_response = response.json()['results']
    return json_response
    
# making the question usable in terms of format
def call_question(cate):
    question = get_questions(1, cate)[0]
    intlist =  [int(i) for i in question['correct_answer'].split() if i.isdigit()]
    if len(intlist) >= 1:
        return call_question(cate)
    else:
        return question

# running a game for players inside the specific lobby
@socketio.on('startgame')
@login_required
def game_start():
    username = session["username"]
    room = current_users[username][0]
    lobby_players = [k for k,v in current_users.items() if v[0] == room]

    # iterating thru the players in the lobby
    for host in lobby_players:
        catlook = current_users[username][2]

        category_list = ['animals', 'video_games', 'celebrities', 'comics', 'general_knowledge',
                            '27', '15', '26', '29', '9']

        for cat in range(int(len(category_list) / 2.0)):
            if category_list[cat] == catlook:
                category = category_list[cat + 5]

        triv = call_question(category)
        correct = triv['correct_answer']
        question = triv["question"]
        answers = triv["incorrect_answers"]
        answers.append(correct)
        random.shuffle(answers)

        current_hosts[room] = host
        correct_answers[room] = correct

        # formatting data to display with the host player
        hostdata = question + " answer: " + correct

        # getting the current amount of points to display
        pointsdata = current_users[username][1]

        # letting javascript run the drawing fase at the client
        emit('fase1', (host, hostdata, pointsdata), broadcast=True, room=room)
        time.sleep(10)

        # letting javascript run the guessing fase at the client
        emit('fase2', (host, answers, question, correct), broadcast=True, room=room)
        time.sleep(10)

    # letting javascript run the endfase of the game finishing everything up
    emit('endfase', broadcast=True)
    # iterating thru players left in te lobby
    for player in lobby_players:
        if player in current_users:
            if current_users[player][0] == room:
                # clearing all the player data
                username = player
                points = current_users[player][1]
                category = current_users[player][2]

                # emitting a request to register the user points
                emit("pointsregister", (username, points, category))

        current_users[player][1] = 0
    time.sleep(10)

############
#
# TimeAttack
#
############

@socketio.on('startTimeAttack')
@login_required
def TimeAttack_start():
    username = session["username"]
    room = current_users[username][0]
    lobby_players = [k for k,v in current_users.items() if v[0] == room]
    current_users[username][4] = 3
    timeout = 20
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        if current_users[username][4] <= 0:
            break
        print("you have", current_users[username][4], "lives")
        catlook = current_users[username][2]
        print("CATEGORY =", catlook)
        category_list = ['animals', 'video_games', 'celebrities', 'comics', 'general_knowledge',
                            '27', '15', '26', '29', '9']
        for cat in range(int(len(category_list) / 2.0)):
            if category_list[cat] == catlook:
                category = category_list[cat + 5]
        triv = call_question(category)
        correct = triv['correct_answer']
        question = triv["question"]
        answers = triv["incorrect_answers"]
        answers.append(correct)
        random.shuffle(answers)
        correct_answers[room] = correct

        pointsdata = current_users[username][1]
        print('pointsdata = ', pointsdata)

        emit('newround', (answers, question, correct), broadcast=True, room=room)
        time.sleep(10)
    print("time's up!")
    emit('endfase', broadcast=True)
    player = lobby_players[0]
    if player in current_users:
        if current_users[player][0] == room:
            username = player
            points = current_users[player][1]
            category = current_users[player][2]

            emit("pointsregister", (username, points, category))
    current_users[player][1] = 0
    time.sleep(10)

##################
#
# einde TimeAttack
#
##################

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
    else:
        if current_users[username][3] == 'TimeAttack':
            current_users[username][4] -= 1
            print("you lost a life!!!")


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
    # Get username from GET
    username = request.args.get("username")

    # Select all usernames from database
    users = scrivdb.execute("SELECT username FROM users")

    # Return False if username length less than 1
    if len(username) < 1:
        return jsonify(False)

    # Return false if username exists
    for user in users:
        if user["username"] == username:
            return jsonify(False)

    # If username length greater than 1 and doesn't exist, return True
    return jsonify(True)


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
    """Show leaderboards of top 10 ranked players in the game, can also filter by categories"""

    # List of the categories to send to HTML
    categories = ["Animals", "Video Games", "Celebrities", "Comics", "General Knowledge"]

    # Show the the sum of the points of all the categories
    total_points = scrivdb.execute("SELECT *, SUM(animals + video_games + celebrities + comics + general_knowledge), username FROM statistics GROUP BY username ORDER BY SUM(animals + video_games + celebrities + comics + general_knowledge) DESC")

    # Show the points per category
    animals_points = scrivdb.execute("SELECT animals, username FROM statistics GROUP BY username ORDER BY animals DESC")
    video_games_points = scrivdb.execute("SELECT video_games, username FROM statistics GROUP BY username ORDER BY video_games DESC")
    celebrities_points = scrivdb.execute("SELECT celebrities, username FROM statistics GROUP BY username ORDER BY celebrities DESC")
    comics_points = scrivdb.execute("SELECT comics, username FROM statistics GROUP BY username ORDER BY comics DESC")
    general_knowledge_points = scrivdb.execute("SELECT general_knowledge, username FROM statistics GROUP BY username ORDER BY general_knowledge DESC")

    return render_template("leaderboards.html", total_points=total_points, categories=categories, animals_points=animals_points, video_games_points=video_games_points,
    celebrities_points=celebrities_points, comics_points=comics_points, general_knowledge_points=general_knowledge_points)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register the user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ask user to input username
        if not request.form.get("username"):
            return apology("must input username", 400)

        # Ask user to input password
        elif not request.form.get("password"):
            return apology("must input password", 400)

        # Password must be at least 7 characters long
        if len(request.form.get("password")) < 7:
            return apology("password must be at least 7 characters long", 400)

        # If passwords do not match, show error
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("passwords must match", 400)

        # Register username and hashed password and insert new member into statistics page
        registration = scrivdb.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
        scrivdb.execute("INSERT INTO statistics (username) VALUES(:username)", username=request.form.get("username"))

        # If username already exists, show error
        if not registration:
            return apology("username already exists, choose another", 400)

        # Get the registered users id
        user_id = scrivdb.execute("SELECT id FROM users WHERE username = :username", username=request.form.get("username"))

        # Remember that the user has logged in
        session["user_id"] = user_id[0]["id"]

        # Redirect user to home page
        return redirect("/login")

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
