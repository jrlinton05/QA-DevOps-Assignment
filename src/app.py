import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, url_for, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import CSRFProtect
from bcrypt import checkpw

import database_wrapper
from logging_config import logger
from schemas.constants import ADMIN_ACCESS_ERROR, DATABASE_CONNECTION_ERROR, CHANNEL_CREATION_SUCCESS, \
    CHANNEL_UPDATE_SUCCESS, CHANNEL_DELETE_SUCCESS, ACCOUNT_CREATION_SUCCESS, CHANNEL_NOT_FOUND_ERROR, \
    INVALID_USER_DETAILS_ERROR
from schemas.exceptions import NameAlreadyExistsException, InvalidArgumentException, DatabaseConnectionException
from schemas.types import User

# Load environment variables to keep the database and app private and secure
load_dotenv()

# Initialise the flask web app
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ["SECRET_KEY"]

# Secure session by protecting cookies and adding timeouts
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') != 'development'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800

# Initialise the flask login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Generate anti-Cross-Site-Request-Forgery token to prevent attacks from foreign sources
csrf = CSRFProtect(app)

# Initialise flask limiter to prevent brute force attacks
limiter = Limiter(app=app, key_func=get_remote_address)


# Prevent multiple common attacks by adding headers to the response
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevents MIME sniffing attacks
    response.headers['X-Frame-Options'] = 'DENY'  # Prevents clickjacking
    response.headers['X-XSS-Protection'] = '1; mode=block'  # Prevents reflected XSS attacks
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'  # Enforces HTTPS
    response.headers['Content-Security-Policy'] =\
        ("default-src 'self'; script-src 'self' cdn.jsdelivr.net; style-src 'self' "
         "cdn.jsdelivr.net fonts.googleapis.com; font-src fonts.gstatic.com")  # Allowlist for necessary loaded content
    return response


# --- User Handling ---
@app.context_processor
def inject_user():
    return dict(user=current_user)


@login_manager.user_loader
def load_user(user_id):
    """Fetch user details from the database and set the current session user."""
    user_data = database_wrapper.get_user_by_user_id(int(user_id))
    if user_data:
        return User(user_id=int(user_id), username=user_data[0], is_admin=user_data[1])
    return None


def admin_required(f):
    """Redirects to the channel browser if the current user does not have admin permissions."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            logger.warning(f"Unauthorised admin access attempt by user: {current_user.username} "
                           f"from IP: {request.remote_addr}")
            flash(ADMIN_ACCESS_ERROR, "error")
            return redirect(url_for('channel_browser'))
        return f(*args, **kwargs)
    return decorated_function


# --- Error Handling ---
@app.errorhandler(DatabaseConnectionException)
def handle_db_error(e):
    return render_template('error.html', message=DATABASE_CONNECTION_ERROR), 503


@app.errorhandler(429)
def rate_limit_exceeded(e):
    return render_template('error.html',
                           message="Too many requests. Please try again in a minute."), 429


# --- App Routing ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/channels')
def channel_browser():
    return render_template('channel-browser.html', channel_data=database_wrapper.get_all_channels())


# --- Channel Management ---
@app.route('/channels/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_channel():
    """Handles the use of the channel creation form.

    GET: Display the channel creation form.
    POST: Validate the entered information and create a new channel.
    """
    if request.method == 'POST':
        logger.info(f"Attempt to create channel by user: {current_user.username} from IP: {request.remote_addr}")
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
    """Handles the use of the channel update form.

    GET: Display the channel update form.
    POST: Validate the entered information and update the appropriate channel.
    """
    if request.method == 'POST':
        logger.info(f"Attempt to update channel by user: {current_user.username} from IP: {request.remote_addr}")
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
    """Routes POST requests towards the database wrapper for deleting channels."""
    logger.info(f"Attempt to delete channel by user: {current_user.username} from IP: {request.remote_addr}")
    try:
        database_wrapper.delete_channel(channel_id)
        flash(CHANNEL_DELETE_SUCCESS)
    except DatabaseConnectionException:
        raise
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for('channel_browser'))


# --- User Registration ---
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    """Handles the use of the user registration form.

    GET: Display the user registration form.
    POST: Validate the entered information and create a new user.
    """
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
@limiter.limit("10 per minute")
def login():
    """Handles the use of the login page.

    GET: Display the login form.
    POST: Validate the entered information and assign the current session user accordingly.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = database_wrapper.get_user_by_username(username)
        if user_data and checkpw(password.encode(), user_data[1].strip().encode()):
            user = User(user_id=user_data[0], username=username, is_admin=user_data[2])
            login_user(user)
            logger.info(f"Successful login for user: {username} from IP: {request.remote_addr}")
            return redirect(url_for('index'))

        logger.warning(f"Failed login attempt for user: {username} from IP: {request.remote_addr}")
        return render_template('login.html', error=INVALID_USER_DETAILS_ERROR, username=username)

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


# Allows local hosting for testing purposes
if __name__ == '__main__':
    app.run()
