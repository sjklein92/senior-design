from flask import Flask, render_template, abort, json, send_file
import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('chimera.default_config')
app.config.from_pyfile('application.cfg')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

import chimera.auth as auth

@app.route('/')
def index():
    if auth.current_user.is_authenticated():
        return render_template('editor.html', user=auth.current_user.get_id())
    else:
        return render_template('banner.html')

app.register_blueprint(auth.module)

def make_json(data, status=200, headers={}):
    default_headers = {"Content-Type": "application/json"}
    default_headers.update(headers)
    return json.dumps(data), status, default_headers

@app.route('/api/files')
@auth.login_required
def files_index():
    return make_json({"foo":"bar"})

@app.route('/api/files/<path:path>')
@auth.login_required
def files_get(path):
    path = os.path.abspath(os.path.join(auth.current_user.folder_path, path))
    if not path.startswith(auth.current_user.folder_path) or not path.startswith(app.config['STORAGE_PATH']):
        return abort(403)
    if not os.path.exists(path):
        return abort(404)
    return send_file(path, 'text/plain')

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

@app.route('/preview/')
@auth.login_required
def preview_base():
    return preview('index.html')

