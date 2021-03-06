from flask import Flask, render_template, abort, json, send_file, request, flash, redirect
import os
import chimera.chigit as git
import subprocess

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
    raw = git.getGitFiles( auth.current_user.folder_path)
    statuses = git.statuses( auth.current_user.folder_path)
    tree1 = {}
    for f in raw:
        parts = f.split(os.path.sep)
        cur = tree1
        for part in parts:
            if not(part in cur):
                cur[part] = {}
            cur = cur[part]
    tree2 = tree_transform(tree1, '', statuses)
    return make_json(tree2["children"])

def tree_transform(tree, name, statuses):
    children = []
    ans = {"text": name.split('/')[-1], "type": "folder"}
    for k in tree:
        if tree[k] == {}:
            # this looks wrong but git doesn't list empty folders
            child = {"text": k, "type": "file", "serverPath": name+"/"+k}
            if child['serverPath'] in statuses:
                st = statuses[child['serverPath']][1]
                if st == 'M':
                    child['icon'] = 'glyphicon glyphicon-pencil'
                elif st == '?':
                    child['icon'] = 'glyphicon glyphicon-plus'
                elif st == 'D':
                    child['icon'] = 'glyphicon glyphicon-remove'
            else:
                child['icon'] = 'glyphicon glyphicon-file'
            children.append(child)
        else:
            children.append(tree_transform(tree[k], name+"/"+k, statuses))
    def cmp(a, b):
        if 'children' in a and not('children' in b):
            return -1
        if 'children' in b and not('children' in a):
            return 1
        if a['text'] > b['text']:
            return 1
        if a['text'] < b['text']:
            return -1
        return 0
    ans["children"] = sorted(children, cmp=cmp)
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

@app.route('/download/<path:path>')
@auth.login_required
def files_download(path):
    path = os.path.abspath(os.path.join(auth.current_user.folder_path, path))
    if not path.startswith(auth.current_user.folder_path) or not path.startswith(app.config['STORAGE_PATH']):
        return abort(403)
    if not os.path.exists(path):
        return abort(404)
    return send_file(path, as_attachment=True)

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

@app.route('/api/generate', methods=['POST'])
@auth.login_required
def generate_preview():
    old_pwd = os.path.abspath(os.curdir)
    os.chdir(auth.current_user.folder_path)
    subprocess.call(["jekyll", "build", "--config", "_config.yml,"+os.path.join(old_pwd,"jekyll_config.yml")])
    os.chdir(old_pwd)
    return make_plain('Updated')

@app.route('/publish/', methods=['GET','POST'])
@auth.permission_required('publish')
def publish():
    if request.method == 'GET':
        statuses = git.statuses(auth.current_user.folder_path)
        files = []
        for f in statuses:
            st = statuses[f][1]
            if st == 'M':
                files.append((f, 'pencil'))
            elif st == '?':
                files.append((f, 'plus'))
            elif st == 'D':
                files.append((f, 'remove'))
        files = sorted(files)
        return render_template('publish.html', files=files)
    else:
        if not('description' in request.form) or not(request.form['description']):
            flash('You must provide a description.', 'danger')
            return redirect('/publish/')
        if git.commit(auth.current_user.folder_path, request.form['description']):
            flash('Published.', 'success')
            return redirect('/')
        else:
            flash('There was an error with publishing. Contact your administrator.', 'danger')
            return redirect('/')
