from flask import Blueprint, redirect, render_template, request, abort, url_for
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from chimera.auth.models import User
from urllib import urlencode
from urlparse import parse_qs
import requests

module = Blueprint('auth', __name__, template_folder='templates')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@module.record_once
def on_load(state):
    global config
    login_manager.init_app(state.app)
    config = state.app.config

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@module.route('/login')
def login():
    state = urlencode({"next": request.args.get('next', '/')})
    print(repr(state))
    # Redirect the user's browser to Google's auth page.
    # We will get a callback with an authorization code or error
    auth_url = config['GOOGLE_OAUTH2_URL']+'auth?'+urlencode({
        "response_type": "code",
        "client_id": config['GOOGLE_OAUTH2_CLIENT_ID'],
        "redirect_uri": url_for('.callback', _external=True),
        "scope": config['GOOGLE_OAUTH2_SCOPE'],
        "state": state
    })
    return redirect(auth_url)

@module.route('/login/callback')
def callback():
    if 'error' in request.args:
        return request.args['error'], 401
    if 'state' in request.args:
        state = parse_qs(request.args['state'])
    else:
        state = {"next": ["/"]}
    print(repr(state))
    # Now exchange the authorization code for an access token and refresh token
    code = request.args['code']
    token_resp = requests.post(config['GOOGLE_OAUTH2_URL']+'token', data={
        "code": code,
        "client_id": config['GOOGLE_OAUTH2_CLIENT_ID'],
        "client_secret": config['GOOGLE_OAUTH2_CLIENT_SECRET'],
        "redirect_uri": url_for('.callback', _external=True),
        "grant_type": "authorization_code"
    }).json()
    if 'error' in token_resp:
        return token_resp.get('error_description', token_resp['error']), 401

    token = token_resp['access_token']
    # Make an API request to get the actual email address
    userinfo_resp = requests.get(config['GOOGLE_API_URL']+'userinfo', params={"alt":"json"},
            headers={"Authorization": "Bearer "+token}).json()
    if 'error' in userinfo_resp:
        return userinfo_resp.get('error_description', userinfo_resp['error']), 401
    email = userinfo_resp['email']

    user = User.get(email)
    if user.is_authenticated():
        user.access_token = token
        user.save()
        login_user(user)
        return redirect(state['next'][0])
    else:
        return "Not authenticated.", 401

@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@module.route('/protected')
@login_required
def protected():
    return 'Secret content which requires login'
