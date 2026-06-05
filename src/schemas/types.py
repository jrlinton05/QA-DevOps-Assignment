from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, username, is_admin):
        self.id = user_id
        self.username = username
        self.is_admin = is_admin
