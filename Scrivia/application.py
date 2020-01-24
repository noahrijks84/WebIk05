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

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, manage_session=False)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
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
    return jsonify(True)

@socketio.on('leaverequest')
@login_required
def on_leave_request():
    username = session["username"]
    if username in current_users:
        current_users[username][0] = None
        current_users[username][1] = 0

@socketio.on('lobbyrequest')
@login_required
def on_lobby_request(lobby):
    username = session["username"]
    join_room(lobby)
    current_users[username] = [lobby, 0, True]

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

@socketio.on('startgame')
@login_required
def game_start():
    username = session["username"]
    room = current_users[username][0]
    lobby_players = [k for k,v in current_users.items() if v[0] == room]
    print(lobby_players)

    for host in lobby_players:
        triv = trivdb.execute("SELECT question, correct, incorrect FROM trivia_a ORDER BY RANDOM() LIMIT 1")
        correct = triv[0]['correct']
        question = triv[0]["question"]
        inc = triv[0]["incorrect"]
        answers = inc.split("'")
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
        print(player + ": " + str(current_users[player][1]))
        current_users[player][1] = 0
    time.sleep(10)

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
    """Return true if username available, else false, in JSON format"""
    # Get username from GET
    username = request.args.get("username")

    # Select all usernames from database
    users = db.execute("SELECT username FROM users")

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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
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
    """Register user"""
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

        # Register username and hashed password
        registration = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        # If username already exists, show error
        if not registration:
            return apology("username already exists, choose another", 400)

        # Get the registered users id
        user_id = db.execute("SELECT id FROM users WHERE username = :username", username=request.form.get("username"))

        # Remember that the user has logged in
        session["user_id"] = user_id[0]["id"]

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