from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.fields.html5 import EmailField
from wtforms.validators import *


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember_me')
    submit_login = SubmitField('Login')


class RegisterForm(FlaskForm):
    surname = StringField("Surname*", validators=[DataRequired()])
    name = StringField("Name*", validators=[DataRequired()])
    nickname = StringField("Login*", validators=[DataRequired()])
    birth_date = StringField("Birthday Date(YYYY-MM-DD)*", validators=[DataRequired()])
    email = EmailField("E-mail*", validators=[DataRequired()])
    password = PasswordField("Password*", validators=[DataRequired()])
    password_again = PasswordField("Repeat Password*", validators=[
        DataRequired(), EqualTo('password', "Passwords must be equal!")])
    submit_register = SubmitField("Register!")


def tag_validate(form, field):
    tags = field.data
    for tag in tags.split(","):
        if not tag:
            continue
        tag = tag.strip()
        if tag[0] == "_":
            raise ValidationError("Tag can't start from underscore.")


class NewNoteForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content (markdown)", validators=[DataRequired()])
    tags = StringField("Tags (comma-separated)", validators=[tag_validate])
    submit_new_note = SubmitField("Create note")


class NoteSearchForm(FlaskForm):
    field = StringField()
    submit_note_search = SubmitField("Search")


class NewAvaForm(FlaskForm):
    select_file = FileField("Load Photo", validators=[DataRequired()])
    submit_new_ava = SubmitField("Load")
