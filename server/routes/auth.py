from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user

from server.helper import settings, username_is_valid
from server.user_models import User

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    # Get user from the database
    user = User.get_by_username(username)

    if user is None:
        flash("Username not found", "alert-danger")
        return(redirect(url_for("main.index")))
    if not user.check_password(password):
        flash("Wrong password", "alert-danger")
        return(redirect(url_for("main.index")))

    # Log the user in then send them back
    login_user(user, remember=remember)
    flash("Logged in successfully", "alert-success")
    return(redirect(url_for("main.index")))

@auth.route("/signup", methods=["POST"])
def signup_post():
    username = request.form.get("username")
    password = request.form.get("password")

    # Make sure username is valid and hasn't been taken
    if not username_is_valid(username):
        flash("Please enter a valid username (only letters, numbers, -, and _)", "alert-warning")
        return(redirect(url_for("main.index")))
    if User.get_by_username(username) is not None:
        flash("Username already taken, please choose another", "alert-warning")
        return(redirect(url_for("main.index")))
    # Make sure the passowrds match
    if request.form.get("password") != request.form.get("confirm-password"):
        flash("Passwords do not match", "alert-danger")
        return(redirect(url_for("main.index")))

    if User.signup(username, password): # Returns True if successful :)
        # Send a confirmation email :)
        # msg = Message(subject="Welcome to Wiki Wall Street!", 
        #               sender=OUTGOING_EMAILS["default"],
        #               recipients=[email])
        # msg.text = render_template("emails/welcome.txt", name=name, server_url=settings.SERVER_URL)
        # msg.html = render_template("emails/welcome.html", name=name, server_url=settings.SERVER_URL)
        # mail.send(msg)
        return(redirect(url_for("main.index")))
    else:
        flash("This username already exists -- please log in instead", "alert-danger")
        return(redirect(url_for("main.index")))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return(redirect(url_for("main.index")))
