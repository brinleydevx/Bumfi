from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField("Content", validators=[DataRequired(), Length(min=20)])
    save_draft = SubmitField("Save Draft")
    publish = SubmitField("Publish")

class CommentForm(FlaskForm):
    content = TextAreaField(
        "Add a comment",
        validators=[DataRequired(), Length(min=1, max=500)]
    )

    submit = SubmitField("Post Comment")
    parent_id = HiddenField()


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    full_name = StringField("Full name", validators=[Length(max=150)])
    bio = TextAreaField("Bio", validators=[Length(max=500)])
    website = StringField("Website", validators=[Optional(), Length(max=255)])
    github = StringField("GitHub", validators=[Optional(), Length(max=255)])
    twitter = StringField("Twitter", validators=[Optional(), Length(max=255)])
    picture = FileField("Profile picture", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only")])
    submit = SubmitField("Save")


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=50)])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")
