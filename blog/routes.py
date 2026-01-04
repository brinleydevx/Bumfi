from flask import Blueprint, render_template, redirect, url_for, flash, abort
from werkzeug.utils import redirect
from flask_login import login_required, current_user, logout_user, login_user
from . import db

from .models import Post, User
from .forms import PostForm

main = Blueprint("main", __name__)

@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            flash("User already exists", "danger")
            return redirect(url_for("main.register"))

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Account created — please login", "success")

        # IMPORTANT — must be returned
        return redirect(url_for("main.login"))

    return render_template("auth/register.html")


# Login
@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully", "success")
            return redirect(url_for("main.home"))

        flash("Invalid username or password", "danger")

    return render_template("auth/login.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("home"))


@main.route("/")
def home():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('home.html', posts=posts)

@main.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        post.author = current_user
        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("main.home"))
    return render_template("create.html", form=form)

@main.route("/post/<int:id>")
def post_detail(id):
    post = Post.query.get_or_404(id)
    return render_template("post_detail.html", post=post)

# post update -- here a user can update/edit their posts
from flask import request

@main.route("/post/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()

    if post.author != current_user:
        abort(403)

    if request.method == "GET":
        # Pre-fill form with existing values
        form.title.data = post.title
        form.content.data = post.content

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data

        db.session.commit()
        flash("Post updated successfully!", "success")

        return redirect(url_for("main.post_detail", id=post.id))

    return render_template("edit.html", form=form, post=post)

