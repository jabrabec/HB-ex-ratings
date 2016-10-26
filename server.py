"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/register', methods=['GET'])
def register_form():
    """Register new user"""
    
    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Register new user"""

    login = request.form.get("login")
    password = request.form.get("password")
    new_user = db.session.query(User).filter(User.email==login).first()
    if new_user:
        # user already exists
        return redirect("/register")
    else:
        # add user to db
        user = User(email=login,password=password)
        db.session.add(user)
        db.session.commit()

    return redirect("/")

@app.route("/login", methods=["GET"])
def show_login():
    """Show login form."""

    if session.get("logged_in_customer_email") == None:
        return render_template("login_form.html")
    else:
        flash("You are already logged in.")
        return redirect("/")


@app.route("/login", methods=["POST"])
def process_login():
    """Log user into site.

    Find the user's login credentials located in the database,
    look up the user, and store them in the session.
    """

    email = request.form.get('login')
    password = request.form.get('password')

    user = db.session.query(User).filter(User.email==email).first()

    if not user:
        flash("No such email address.")
        return redirect('/login')

    if user.password != password:
        flash("Incorrect password.")
        return redirect("/login")

    session["logged_in_customer_email"] = user.email
    flash("Logged in.")
    # rated_movies = db.session.

    return render_template("/user_detail.html", user=user)

@app.route("/logout")
def process_logout():
    """Log user out."""


    if session.get("logged_in_customer_email") == None:
        flash("You are not logged in.")
        return redirect("/")
    else:
        del session["logged_in_customer_email"]
        flash("Logged out.")
        return redirect("/")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)


    
    app.run(port=5003)
