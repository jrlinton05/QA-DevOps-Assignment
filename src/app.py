import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, url_for, redirect
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from bcrypt import checkpw

import database_wrapper
from schemas.constants import ADMIN_ACCESS_ERROR, DATABASE_CONNECTION_ERROR, CHANNEL_CREATION_SUCCESS, \
    CHANNEL_UPDATE_SUCCESS, CHANNEL_DELETE_SUCCESS, ACCOUNT_CREATION_SUCCESS, CHANNEL_NOT_FOUND_ERROR, \
    INVALID_USER_DETAILS_ERROR
from schemas.exceptions import NameAlreadyExistsException, InvalidArgumentException, DatabaseConnectionException
from schemas.types import User

load_dotenv()

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ["SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.context_processor
def inject_user():
    return dict(user=current_user)


@login_manager.user_loader
def load_user(user_id):
    user_data = database_wrapper.get_user_by_user_id(int(user_id))
    if user_data:
        return User(user_id=int(user_id), username=user_data[0], is_admin=user_data[1])
    return None


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash(ADMIN_ACCESS_ERROR, "error")
            return redirect(url_for('channel_browser'))
        return f(*args, **kwargs)
    return decorated_function


@app.errorhandler(DatabaseConnectionException)
def handle_db_error(e):
    return render_template('error.html', message=DATABASE_CONNECTION_ERROR), 503


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/channels')
def channel_browser():
    return render_template('channel-browser.html', channel_data=database_wrapper.get_all_channels())


@app.route('/channels/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_channel():
    if request.method == 'POST':
        channel_name = request.form['channel_name']
        channel_price = request.form['channel_price']

        try:
            database_wrapper.add_new_channel(channel_name, channel_price)
            flash(CHANNEL_CREATION_SUCCESS)
            return redirect(url_for('channel_browser'))
        except (NameAlreadyExistsException, InvalidArgumentException) as e:
            return render_template('channel-add.html', error=str(e),
                                   channel_name=channel_name, channel_price=channel_price)
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for('channel_browser'))
    return render_template('channel-add.html')


@app.route('/channels/<int:channel_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def update_channel(channel_id):
    if request.method == 'POST':
        channel_name = request.form['channel_name']
        channel_price = request.form['channel_price']

        try:
            database_wrapper.update_channel_details(channel_id, channel_name, channel_price)
            flash(CHANNEL_UPDATE_SUCCESS)
            return redirect(url_for('channel_browser'))
        except (NameAlreadyExistsException, InvalidArgumentException) as e:
            return render_template('channel-update.html', error=str(e),
                                   channel_id=channel_id, channel_name=channel_name, channel_price=channel_price)
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for('channel_browser'))

    data = database_wrapper.get_channel_data(channel_id)
    if data is None:
        flash(CHANNEL_NOT_FOUND_ERROR, "error")
        return redirect(url_for('channel_browser'))
    return render_template('channel-update.html', channel_id=channel_id,
                           channel_name=data[0], channel_price=data[1])


@app.route('/channels/<int:channel_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_channel(channel_id):
    try:
        database_wrapper.delete_channel(channel_id)
        flash(CHANNEL_DELETE_SUCCESS)
    except DatabaseConnectionException:
        raise
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('channel_browser'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            database_wrapper.add_new_user(username, password)
            flash(ACCOUNT_CREATION_SUCCESS)
            return redirect(url_for('login'))
        except NameAlreadyExistsException as e:
            return render_template('register.html', error=str(e), username=username)
        except InvalidArgumentException as e:
            return render_template('register.html', error=str(e), username=username)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = database_wrapper.get_user_by_username(username)
        if user_data and checkpw(password.encode(), user_data[1].strip().encode()):
            user = User(user_id=user_data[0], username=username, is_admin=user_data[2])
            login_user(user)
            return redirect(url_for('index'))

        return render_template('login.html', error=INVALID_USER_DETAILS_ERROR, username=username)

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
