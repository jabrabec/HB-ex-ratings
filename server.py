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


@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


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
    # alternate session storage for logged in user:
    # session["logged_in_user"] = user
    flash("Logged in.")

    return render_template("/user_detail.html", user=user)
    # return redirect()


@app.route("/users/<user_id>")
def user_detail(user_id):
    """User details page."""

    # user = db.session.query(User).filter(User.user_id==user_id).first()
    user = User.query.get(user_id)
    return render_template("/user_detail.html", user=user)


@app.route("/movies/<movie_id>")
def movie_detail(movie_id):
    """Movie details page."""

    movie = Movie.query.get(movie_id)

    user_rating = None;

    user_email = session.get("logged_in_customer_email")

    if user_email:
        user_id = User.query.filter(User.email==user_email).first().user_id
        user_rating = Rating.query.filter(Rating.movie_id==movie_id, Rating.user_id==user_id).first()
    
    return render_template("/movie_detail.html", movie=movie, user_rating=user_rating)


@app.route("/movie_score/<movie_id>", methods=['POST'])
def process_score(movie_id):
    """Movie score saved to DB."""
    
    score = int(request.form.get('score'))

    user_email = session.get("logged_in_customer_email")
    user_id = User.query.filter(User.email==user_email).first().user_id
    new_score = Rating(movie_id=movie_id, user_id=user_id, score=score)
    db.session.add(new_score)
    db.session.commit()

    return redirect("/movies/%s" %movie_id)


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
