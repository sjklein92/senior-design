from flask import Flask, render_template
import chimera.auth as auth

app = Flask(__name__)
app.config.from_object('config')

import yaml
f = open('config.yml')
conf = yaml.safe_load(f)
f.close()
del(f)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return "In main, User: %s"%auth.current_user.get_id()

app.register_blueprint(auth.module)
