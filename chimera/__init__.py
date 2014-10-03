from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object('config')

import yaml
f = open('config.yml')
conf = yaml.load(f)
f.close()
del(f)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
