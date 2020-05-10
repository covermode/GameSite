from flask import Flask
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from flask_ngrok import run_with_ngrok
import flask
import datetime

from data.db_session import create_session, global_init
from data.__all_models import *
from data import note_resource, user_resource
from lib.forms import LoginForm, RegisterForm, NoteSearchForm, NewNoteForm, NewAvaForm
from lib.log import log


def make_path(rel_path):
    """Common function for making relative path absolute"""
    import os
    return os.path.join(*os.path.split(__file__)[:-1], *os.path.split(rel_path))


def unmark(mark):
    """Generates html from markdown, making it safe to use as possible"""
    import markdown
    from lxml.html.clean import clean_html
    ret_html = clean_html(markdown.markdown(mark, safe_mode=True))
    return ret_html


USE_NGROK = True

app = Flask(__name__)
api = Api(app)
if USE_NGROK:
    run_with_ngrok(app)
app.config["SECRET_KEY"] = "game_site_secret_key_yeah_bro"
db = make_path("data/db/data.sqlite")           # path to database
badge_ico_src = "/static/image/badge_ico"       # path to directory with all badge pics
user_avas_src = "/static/image/user_avas"       # path to directory with all user icons
support_email = "support@example.com"
CONTACT_INFO_HTML = """
<p>Сайт был создан на основе базы GameSite</p>
<p>(Латыпов Илья)</p>"""    # (WARNING: DO NOT USE LINKS TO OTHER INSECURE AND UNTRUSTED RESOURCES)

login_manager = LoginManager(app)
login_manager.init_app(app)


class BaseHelper:
    """Adds some values to next rendered template. (for 'base.html')"""
    def __init__(self):
        self.ret = {}

    def add_info(self, key, value):
        assert key not in self.ret
        self.ret[key] = value

    def make_info(self):
        """Refuses values. Contains some values for 'base.html' template"""
        ret = {
            'name_of_game': "GameSite",
            'background_image': flask.url_for("static", filename="image/bg.png"),
            'logo': flask.url_for("static", filename="image/logo.png"),
            **self.ret
        }
        self.ret = {}
        return ret


base_info = BaseHelper()


def login_handler(func):
    """Decorator for handling and creating login form on base page.
    Shouldn't be used with @login_required"""
    def wrapper(*args, **kwargs):
        login_form = LoginForm()
        base_info.add_info("login_form", login_form)
        if login_form.submit_login.data and login_form.validate():
            session = create_session()
            user = session.query(User).filter(User.email == login_form.email.data).first()
            if user and user.check_password(login_form.password.data):
                login_user(user, remember=login_form.remember_me.data)
                base_info.add_info("page_message", "Logged in")
            else:
                base_info.add_info("page_error", "Wrong password or login")
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@app.route("/", methods=["GET", "POST"])
@login_handler
def index():
    """Index page. Loads note with tag '__main__' and displays its content"""
    log.debug("Loaded index page")

    session = create_session()
    main_tag = session.query(Tag).filter(Tag.name == "__main__").first()
    main_note = session.query(Note).filter(Note.tags.contains(main_tag)).first()
    if main_note is None:
        main_note_content = ""
    else:
        main_note_content = main_note.content
    return flask.render_template(
        "index.html", title="GameSite", main_content=unmark(main_note_content),
        **base_info.make_info())


@app.route("/about", methods=["GET", "POST"])
@login_handler
def about():
    """Page 'about'. To edit following information edit CONTACT_INFO_HTML (WARNING: DO NOT USE
    LINKS TO OTHER INSECURE AND UNTRUSTED RESOURCES)"""
    log.debug("Loaded 'about' page")

    return flask.render_template("about.html", info=CONTACT_INFO_HTML, title="About",
                                 **base_info.make_info())


@app.route("/register", methods=["GET", "POST"])
def register():
    """page 'register'. Creates new user. todo Captcha isn't implemented"""
    log.debug("Loaded 'register' page")

    register_form = RegisterForm()
    if register_form.validate_on_submit():
        session = create_session()
        if session.query(User).filter(User.email == register_form.email.data).first():
            return flask.render_template(
                "register.html", title="Failure", register_form=register_form,
                page_error="This e-mail already occupied", **base_info.make_info())

        kwargs = {
            "surname": register_form.data["surname"],
            "name": register_form.data["name"],
            "nickname": register_form.data["nickname"],
            "age": int(
                (datetime.datetime.now().date() - datetime.datetime.fromisoformat(
                    register_form.data["birth_date"]).date()).days // 365.25),
            "email": register_form.data["email"],
            "password": register_form.data["password"],
        }
        new = User.generate_myself(**kwargs)
        session.add(new)
        session.commit()
        log.info(f"Registered user [{new.id}] '{new.nickname}'")
        base_info.add_info("page_message", "Successfully registered")
        return flask.redirect("/")
    return flask.render_template(
        "register.html", title="Register", register_form=register_form, **base_info.make_info())


@app.route("/news", methods=["GET", "POST"])
@login_handler
def news():
    """Page 'news'. Loads and displays all notes with tag '__news__' and filter it by search query
    from internal search field"""
    log.debug("Loaded 'news' page")

    search_form = NoteSearchForm()
    search_query = ""
    if search_form.submit_note_search.data and search_form.validate():
        search_query = search_form.field.data

    session = create_session()
    news_tag = session.query(Tag).filter(Tag.name == "__news__").first()
    maybe_tag = session.query(Tag).filter(Tag.name.like("%{}%".format(search_query))).first()
    if search_query and maybe_tag:
        opera = Note.tags.contains(maybe_tag)
    else:
        opera = True
    notes = list(reversed(session.query(Note).filter(Note.tags.contains(news_tag),
                                                     opera).all()))
    return flask.render_template("notes_show.html", title="New", notes=notes,
                                 search_form=search_form, **base_info.make_info())


@app.route("/forum", methods=["GET", "POST"])
@login_handler
def forum():
    """Page 'forum'. Contains note display (except notes with system tags like '__main__' or '__new__')
    and filter them by search query from internal search field"""
    log.debug("Loaded 'forum' page")

    search_form = NoteSearchForm()
    search_query = ""
    if search_form.submit_note_search.data and search_form.validate():
        search_query = search_form.field.data

    session = create_session()
    maybe_tag = session.query(Tag).filter(Tag.name.notlike("\\_\\_%\\_\\_", escape="\\"),
                                          Tag.name.like("%{}%".format(search_query))).first()
    if search_query and maybe_tag:
        opera = Note.tags.contains(maybe_tag)
    else:
        opera = False
    notes = list(reversed(list(filter(
        lambda n: all([t.name[0] != "_" for t in n.tags]),
        session.query(Note).filter(Note.title.like("%{}%".format(search_query)) |
                                   opera).all()))))
    return flask.render_template("notes_show.html", title="Forum", notes=notes,
                                 search_form=search_form, **base_info.make_info())


@app.route("/read_note/<int:note_id>", methods=["GET", "POST"])
@login_handler
def read_note(note_id: int):
    """Page 'read_note'. Allows to see note's content, converted from markdown to html
    todo Upgrade safeness system, or provide own editor instead of markdown raw data pasta"""
    log.debug("Loaded 'debug' page")

    session = create_session()
    note = session.query(Note).get(note_id)
    return flask.render_template(
        "note.html", title=note.title, note_title=note.title, note_rating=note.rating,
        author_nickname=note.author.nickname, author_id=note.author.id, note_id=note.id,
        author_badges=note.author.badges, note_content=unmark(note.content),
        **base_info.make_info())


@app.route("/upvote/<note_id>")
@login_required
def upvote(note_id):
    """Page 'upvote'. Due the ability to call it infinitely many times,
    note's rating isn't actual thing"""
    session = create_session()
    note = session.query(Note).get(note_id)
    note.rating += 1
    session.commit()
    return flask.redirect(f"/read_note/{note_id}")


@app.route("/downvote/<note_id>")
@login_required
def downvote(note_id):
    """Page 'downvote'. Due the ability to call it infinitely many times,
    note's rating isn't actual thing"""
    session = create_session()
    note = session.query(Note).get(note_id)
    note.rating -= 1
    session.commit()
    return flask.redirect(f"/read_note/{note_id}")


@app.route("/new_note", methods=["GET", "POST"])
@login_required
def new_note():
    """Page 'new_note'. Note creating interface.
    At current version provides raw markdown data paste, which could be unsafe"""
    log.debug("Loaded 'new_note' page")

    form = NewNoteForm()
    if form.validate_on_submit():
        user = current_user
        session = create_session()
        tags = form.data["tags"]
        new_tags = []
        for tag in tags.split(","):
            if not tag:
                continue
            tag = tag.strip(" ")
            new_tag = session.query(Tag).filter(Tag.name == tag).first()
            if not new_tag:
                new_tag = Tag()
                new_tag.name = tag
                session.add(new_tag)
            new_tags.append(new_tag)

        new = Note.generate_myself(form.data["title"], form.data["content"],
                                   user.id, new_tags)

        session.add(new)
        session.commit()
        log.info(f"Created new note [{new.id}] '{new.title}' by '{new.author.name}'")
        return flask.redirect("/forum")
    return flask.render_template("new_note.html", title="New note", new_note_form=form,
                                 **base_info.make_info())


@app.route("/office")
@login_required
def office():
    """Page 'office'. Show user his own information, also private info, like name, email"""
    log.debug("Loaded 'office' page")

    user = current_user
    if user.ava:
        ava = user_avas_src + "/" + user.ava
    else:
        ava = ""

    return flask.render_template(
        "office.html", title=user.nickname, user_name=user.surname + " " + user.name,
        user_email=user.email, ava_link=ava,
        **base_info.make_info()
    )


@app.route("/user_profile/<user_id>")
@login_handler
def user_profile(user_id):
    """Page 'user_profile'. Shows anyone public user information (nickname + ava picture)"""
    log.debug("Loaded 'user_profile' page")

    session = create_session()
    user = session.query(User).get(user_id)
    if user.ava:
        ava = user_avas_src + "/" + user.ava
    else:
        ava = ""

    return flask.render_template("user_profile.html", title=user.nickname, ava_link=ava,
                                 user_nickname=user.nickname, **base_info.make_info())


@app.route("/change_ava", methods=["GET", "POST"])
@login_required
def change_ava():
    """Page 'change_ava'. Profile pic changing form."""
    log.debug("Loaded 'change_ava' page")

    form = NewAvaForm()
    if form.validate_on_submit():
        session = create_session()
        user = session.query(User).get(current_user.id)
        form.select_file.data.save(f"static/image/user_avas/ava_{user.name}.png")
        user.ava = f"ava_{user.name}.png"
        session.commit()
        return flask.redirect("/office")
    return flask.render_template("change_ava.html", title="Change Ava", change_ava_form=form,
                                 **base_info.make_info())


@app.route("/donate")
@login_required
def donate():
    """Page 'donate'. Unimplemented at the moment so game isn't corrupted by sins of
    microtransactions"""
    log.debug("Loaded 'donate' page")

    # user = current_user
    return flask.render_template(
        "donate.html", title="Donate", **base_info.make_info()
    )


@app.route("/support", methods=["GET", "POST"])
@login_handler
def support():
    """Page 'support'. Contains contact info."""
    log.debug("Loaded 'support' page")

    return flask.render_template(
        "support.html", title="Support", support_email=support_email, **base_info.make_info()
    )


@app.route("/download", methods=["GET", "POST"])
@login_handler
def download():
    """Page 'download'. Contains link to download game"""
    log.debug("Loaded 'download' page")

    return flask.render_template("download.html", title="Download", **base_info.make_info())


@app.route("/download_")
def download_():
    """Link to download game"""
    return flask.send_from_directory("source", "game.exe", as_attachment=True)


@app.route("/api")
def api_help():
    """Page 'api'. Show general api help. (To edit go to following html 'api_help.hmtl' and edit
    it)"""
    return flask.render_template("api_help.html")


@app.route('/logout')
@login_required
def logout():
    """Link to logout user"""
    logout_user()
    return flask.redirect("/")


def main():
    global_init(db)

    api.add_resource(note_resource.NoteResource, '/api/note/<int:note_id>')
    api.add_resource(note_resource.NoteListResource, '/api/notes')
    api.add_resource(user_resource.UserResource, '/api/user/<int:user_id>')
    api.add_resource(user_resource.UserListResource, '/api/users')
    if USE_NGROK:
        app.run()
    else:
        app.run("localhost", 5000)
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
