from flask import Flask, render_template, abort, json, send_file, request
import os
import chimera.chigit as git

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('chimera.default_config')
app.config.from_pyfile('application.cfg')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

import chimera.auth as auth

@app.context_processor
def additional_context():
    if auth.current_user.is_authenticated():
        return {"user_id": auth.current_user.get_id()}
    else:
        return {}

@app.route('/')
def index():
    if auth.current_user.is_authenticated():
        return render_template('editor.html')
    else:
        return render_template('banner.html')

app.register_blueprint(auth.module)

import chimera.users
app.register_blueprint(chimera.users.module, url_prefix='/users')

def make_json(data, status=200, headers={}):
    default_headers = {"Content-Type": "application/json"}
    default_headers.update(headers)
    return json.dumps(data), status, default_headers

def make_plain(data, status=200, headers={}):
    default_headers = {"Content-Type": "text/plain"}
    default_headers.update(headers)
    return data, status, default_headers

@app.route('/api/files')
@auth.login_required
def files_index():
    raw = git.getGitFiles(None, auth.current_user.folder_path)
    tree1 = {}
    for f in raw:
        parts = f.split(os.path.sep)
        cur = tree1
        for part in parts:
            if not(part in cur):
                cur[part] = {}
            cur = cur[part]
    tree2 = tree_transform(tree1, '/')
    return make_json(tree2["children"])

def tree_transform(tree, name):
    children = []
    ans = {"text": name}
    for k in tree:
        if tree[k] == {}:
            children.append({"text": k, "icon": "leaf"})
        else:
            children.append(tree_transform(tree[k], k))
    ans["children"] = sorted(children)
    return ans

@app.route('/api/files/<path:path>')
@auth.login_required
def files_get(path):
    path = os.path.abspath(os.path.join(auth.current_user.folder_path, path))
    if not path.startswith(auth.current_user.folder_path) or not path.startswith(app.config['STORAGE_PATH']):
        return abort(403)
    if not os.path.exists(path):
        return abort(404)
    return send_file(path, 'text/plain')

@app.route('/api/files/<path:path>', methods=['PUT'])
@auth.login_required
def files_put(path):
    path = os.path.abspath(os.path.join(auth.current_user.folder_path, path))
    if not path.startswith(auth.current_user.folder_path) or not path.startswith(app.config['STORAGE_PATH']):
        return abort(403)
    with open(path, 'wb') as f:
        f.write(request.data)
    return make_plain('Updated')

@app.route('/api/files/<path:path>', methods=['DELETE'])
@auth.login_required
def files_delete(path):
    path = os.path.abspath(os.path.join(auth.current_user.folder_path, path))
    if not path.startswith(auth.current_user.folder_path) or not path.startswith(app.config['STORAGE_PATH']):
        return abort(403)
    if not os.path.exists(path):
        return abort(404)
    os.remove(path)
    return make_plain('Removed')

@app.route('/preview/', defaults={'path':'index.html'})
@app.route('/preview/<path:path>')
@auth.login_required
def preview(path):
    path = os.path.abspath(os.path.join(auth.current_user.folder_path, '_site', path))
    if not path.startswith(os.path.join(auth.current_user.folder_path, '_site')) or not path.startswith(app.config['STORAGE_PATH']):
        return abort(403)
    if os.path.isdir(path):
        path = os.path.join(path, 'index.html')
    if not os.path.exists(path):
        return abort(404)
    return send_file(path)
