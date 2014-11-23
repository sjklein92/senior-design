from flask import Flask, render_template

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('chimera.default_config')
app.config.from_pyfile('application.cfg')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

import chimera.auth as auth

@app.route('/')
def index():
    return "In main, User: %s"%auth.current_user.get_id()

app.register_blueprint(auth.module)