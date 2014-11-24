import chimera.auth as auth
from chimera.auth import User
from flask import Blueprint, abort, redirect, render_template, request, flash, json, url_for

module = Blueprint('users', __name__, template_folder='templates')

def make_json(data, status=200, headers={}):
    default_headers = {"Content-Type": "application/json"}
    default_headers.update(headers)
    return json.dumps(data), status, default_headers

@module.record_once
def on_load(state):
    global config
    config = state.app.config

@module.route('/')
@auth.permission_required('users:index')
def index():
    return render_template('index.html', users=User.all_ids())

@module.route('/', methods=['POST'])
@module.route('/new')
@auth.permission_required('users:create')
def create():
    if request.method == 'POST':
        return "TODO"
    else:
        return render_template('new.html')

@module.route('/<id>')
@auth.login_required
def edit(id):
    if id != auth.current_user.get_id() and not(auth.current_user.has_permission('users:show')):
        flash("You don't have permission for that.", 'danger')
        return redirect('/')
    user = User.get(id)
    if not(user.is_authenticated()):
        return abort(404)
    if auth.current_user.has_permission('users:edit'):
        return render_template('edit.html', user=user)
    else:
        return render_template('show.html', user=user)

@module.route('/<id>', methods=['PUT'])
@auth.permission_required('users:edit')
def update(id):
    return "update "+id

@module.route('/<id>', methods=['DELETE'])
@auth.permission_required('users:delete')
def delete(id):
    return "delete "+id
