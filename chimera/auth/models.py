import flask.ext.login

class User(flask.ext.login.UserMixin):
    @staticmethod
    def get(email):
        return User(email)

    def __init__(self, email):
        self.id = email
