from datetime import datetime
from email.policy import default

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from blog import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True, default='default.png')
    full_name = db.Column(db.String(150), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)

    # ONE relationship definition
    posts = db.relationship("Post", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ✅ own PK
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    # ✅ foreign key points to user.id
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Post {self.title}>"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    date_created = db.Column(
        db.DateTime, default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    post_id = db.Column(
        db.Integer,
        db.ForeignKey("post.id"),
        nullable=False
    )

    author = db.relationship(
        "User",
        backref=db.backref("comments", lazy=True)
    )

    post = db.relationship(
        "Post",
        backref=db.backref("comments", lazy=True)
    )

    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)
