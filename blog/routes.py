from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app
from werkzeug.utils import redirect, secure_filename
from flask_login import login_required, current_user, logout_user, login_user
from . import db

import os
import secrets

from .models import Post, User, Comment
from .forms import PostForm, CommentForm, EditProfileForm, RequestResetForm, ResetPasswordForm
from itsdangerous import URLSafeTimedSerializer

main = Blueprint("main", __name__)

@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Use minimal-entity query to avoid selecting model columns that may not exist yet
        existing = db.session.query(User.id).filter(
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
        return redirect(url_for("main.home"))

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

# User Profile Page
@main.route("/user/<string:username>")
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts

    return render_template(
        "profile.html",
        user=user,
        posts=posts
    )


def save_profile_picture(file_storage):
    if not file_storage:
        return None

    filename = secure_filename(file_storage.filename)
    _, ext = os.path.splitext(filename)
    unique = secrets.token_hex(8)
    new_name = f"{unique}{ext}"

    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, new_name)
    file_storage.save(path)

    return new_name

@main.route("/")
def landing_page():
    return render_template("landing_page.html")

@main.route("/home")
def home():
    page = request.args.get("page", 1, type=int)

    posts = Post.query \
        .filter(Post.is_published == True) \
        .order_by(Post.date_created.desc()) \
        .paginate(page=page, per_page=5)

    return render_template("home.html", posts=posts)

@main.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():

        if form.publish.data:
            is_published = True
        elif form.save_draft.data:
            is_published = False
        else:
            is_published = False  # safety fallback

        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            is_published=is_published
        )

        db.session.add(post)
        db.session.commit()

        flash(
            "Post published!" if is_published else "Draft saved.",
            "success"
        )

        return redirect(
            url_for("main.home") if is_published
            else url_for("main.user_profile", username=current_user.username)
        )

    return render_template("create.html", form=form)


@main.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = EditProfileForm()

    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.full_name.data = current_user.full_name
        form.bio.data = current_user.bio

    if form.validate_on_submit():
        # handle picture
        if form.picture.data:
            pic_name = save_profile_picture(form.picture.data)
            if pic_name:
                current_user.profile_image = pic_name

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        db.session.commit()

        flash('Account updated.', 'success')
        return redirect(url_for('main.account'))

    return render_template('edit_account.html', form=form)


def send_reset_email(user, token):
    # Simple fallback: print link to console and flash message.
    reset_url = url_for('main.reset_token', token=token, _external=True)
    # In production, integrate Flask-Mail or other mail provider.
    print(f"Password reset link for {user.email}: {reset_url}")
    flash('If an account exists for that email, a reset link has been sent (check console in dev).', 'info')


@main.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps({'user_id': user.id})
            send_reset_email(user, token)

        # Always flash the same message to avoid revealing accounts
        return redirect(url_for('main.login'))

    return render_template('reset_request.html', form=form)


@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)
        user_id = data.get('user_id')
    except Exception:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('main.reset_request'))

    user = User.query.get(user_id)
    if not user:
        flash('Invalid token', 'warning')
        return redirect(url_for('main.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated. Please log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('reset_token.html', form=form)

# Post Delete route
@main.route("/post/<int:post_id>delete", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Ownership Verify
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully.", "success")
    return redirect(url_for("main.home"))

@main.route("/post/<int:id>", methods=["GET", "POST"])
def post_detail(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Login to comment", "warning")
            return redirect(url_for("main.login"))

        parent_id = None
        # form.parent_id will be populated if this is a reply
        try:
            parent_id = int(form.parent_id.data) if form.parent_id.data else None
        except Exception:
            parent_id = None

        comment = Comment(
            content=form.content.data,
            author=current_user,
            post=post,
            parent_id=parent_id
        )

        db.session.add(comment)
        db.session.commit()

        flash("Comment added", "success")
        return redirect(url_for("main.post_detail", id=id))

    return render_template(
        "post_detail.html",
        post=post,
        form=form
    )

@main.route("/comment/<int:id>/delete")
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)

    if comment.author != current_user:
        abort(403)

    post_id = comment.post.id

    db.session.delete(comment)
    db.session.commit()

    flash("Comment deleted", "success")
    return redirect(url_for("main.post_detail", id=post_id))


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

