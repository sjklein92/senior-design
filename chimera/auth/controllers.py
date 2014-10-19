from flask import Blueprint, redirect, render_template, request, abort
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from chimera.auth.models import User

module = Blueprint('auth', __name__, template_folder='templates')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@module.record_once
def on_load(state):
    login_manager.init_app(state.app)

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@module.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        print(request.form)
        u = load_user(request.form.get('email'))
        login_user(u)
        return redirect(request.args.get('next', '/'))
    else:
        return render_template('login.html')

@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@module.route('/protected')
@login_required
def protected():
    return 'Secret content which requires login'
