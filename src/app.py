import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, url_for, redirect

import database_wrapper
from schemas.exceptions import NameAlreadyExistsException, InvalidArgumentException, DatabaseConnectionException

load_dotenv()

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ["SECRET_KEY"]


# Temporary user - remove after setting up flask-login system
@app.context_processor
def inject_user():
    return {'user': {'is_authenticated': False}}


@app.errorhandler(DatabaseConnectionException)
def handle_db_error(e):
    return render_template('error.html', message="Unable to connect to database"), 503


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/channels')
def channel_browser():
    return render_template('channel-browser.html', channel_data=database_wrapper.get_all_channels())


@app.route('/channels/create', methods=['GET', 'POST'])
def create_channel():
    if request.method == 'POST':
        channel_name = request.form['channel_name']
        channel_price = request.form['channel_price']

        try:
            database_wrapper.add_new_channel(channel_name, channel_price)
            flash("Channel created successfully")
            return redirect(url_for('channel_browser'))
        except (NameAlreadyExistsException, InvalidArgumentException) as e:
            return render_template('channel-add.html', error=str(e),
                                   channel_name=channel_name, channel_price=channel_price)
    return render_template('channel-add.html')


@app.route('/channels/<int:channel_id>/edit', methods=['GET', 'POST'])
def update_channel(channel_id):
    if request.method == 'POST':
        channel_name = request.form['channel_name']
        channel_price = request.form['channel_price']

        try:
            database_wrapper.update_channel_details(channel_id, channel_name, channel_price)
            flash("Channel updated successfully")
            return redirect(url_for('channel_browser'))
        except (NameAlreadyExistsException, InvalidArgumentException) as e:
            return render_template('channel-update.html', error=str(e),
                                   channel_id=channel_id, channel_name=channel_name, channel_price=channel_price)

    data = database_wrapper.get_channel_data(channel_id)
    if data is None:
        flash("Channel not found", "error")
        return redirect(url_for('channel_browser'))
    return render_template('channel-update.html', channel_id=channel_id,
                           channel_name=data[0], channel_price=data[1])


@app.route('/login')
def login():
    return "Under Construction"


@app.route('/account')
def account():
    return "Under Construction"


if __name__ == '__main__':
    app.run()
