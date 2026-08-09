from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.auth.forms import RegistrationForm, LoginForm, ProfileForm

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
        )
        user.set_password(form.password.data)
        # First user becomes admin
        if User.query.count() == 0:
            user.is_admin = True
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Your account was created! Welcome to the blog.", "success")
        return redirect(url_for("main.index"))
    return render_template("auth/register.html", form=form, title="Register")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            flash("You have been logged in!", "success")
            return redirect(next_page) if next_page else redirect(url_for("main.index"))
        flash("Login failed. Check your email and password.", "danger")
    return render_template("auth/login.html", form=form, title="Login")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("auth.profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.bio.data = current_user.bio
    return render_template("auth/profile.html", form=form, title="Profile")


@auth.route("/user/<username>")
def public_profile(username):
    from app.models import Post

    user = User.query.filter_by(username=username).first_or_404()
    posts = (
        user.posts.filter_by(is_published=True)
        .order_by(Post.timestamp.desc())
        .all()
    )
    return render_template("auth/public_profile.html", user=user, posts=posts)
