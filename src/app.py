import os
from dotenv import load_dotenv
from flask import Flask, render_template

import database_wrapper


load_dotenv()

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ["SECRET_KEY"]


# Temporary user - remove after setting up flask-login system
@app.context_processor
def inject_user():
    return {'user': {'is_authenticated': False}}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/channels')
def channel_browser():
    return render_template('channel-browser.html', channel_data=database_wrapper.get_all_channels())


@app.route('/channels/create')
def create_channel():
    return "Under Construction"


@app.route('/login')
def login():
    return "Under Construction"


@app.route('/account')
def account():
    return "Under Construction"


if __name__ == '__main__':
    app.run()
