from flask import g, Flask, request, send_file, redirect, session, jsonify, abort
from flask import render_template as render_template_default
import os
import re

from flask import Response
from jinja2 import Template, FunctionLoader, Environment, BaseLoader
from flask import Flask
import mimetypes
import datetime
from flaskext.markdown import Markdown
import zipfile
import getopt
import sys
import pydotenv
env = pydotenv.Environment()

# NOTE: Переменные, Приложение flask(app)
app = Flask(__name__)

config = {}
app.config.from_mapping(config)

MD_PATH = "./md"
PORT = 5022
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, 'd:', ['mpath='])
    for o, a in opts:
        if o == "-d":
            MD_PATH = a
            # sys.argv = list(filter(lambda x: x[0]=="-d", sys.argv))
        if o == "-p":
            PORT = a
    sys.argv = sys.argv[:1]
except getopt.GetoptError:
    # Print a message or do something useful
    print('[E] Something went wrong!')
    sys.exit(2)

MD_PATH=env.get('MD_PATH', "./md")
__DEBUG__ = env.get('__DEBUG__', False)
STATIC_PATH = "/static"
if (__DEBUG__):
    STATIC_PATH = "/zip/static"

oMarkdown = Markdown(app)

def readfile(sFilePath):
    if (__DEBUG__):
        return open(sFilePath, 'rb').read()
    else:
        with zipfile.ZipFile(os.path.dirname(__file__)) as z:
            # print(z.namelist())
            with z.open(sFilePath) as f:
                print("[!] "+f.name)
                # print("[!] "+f.read().decode("utf-8"))
                return f.read()
        return "ERROR"

def load_template(name):
    return readfile("templates/"+name).decode("utf-8")

oTempFunctionLoader = FunctionLoader(load_template)

def render_template(name, **kwargs):
    if __DEBUG__:
        return render_template_default(name, **kwargs)
    else:
        data = load_template(name)
        tpl = Environment(loader=oTempFunctionLoader).from_string(data)
        return tpl.render(**kwargs)

@app.route("/zip/static/<path:path>", methods=['GET', 'POST'])
def zip_static(path):
    oR = Response(readfile("static/"+path), mimetype=mimetypes.guess_type(path)[0])
    oR.headers['Cache-Control'] = 'max-age=60480000, stale-if-error=8640000, must-revalidate'
    return oR

@app.route("/<path:path>", methods=['GET', 'POST'])
def markdown_file(path):
    if path == "" or re.search(r"/$", path):
        path = os.path.join(MD_PATH, path, "index.md")
    else:
        path = os.path.join(MD_PATH, path)
    oR = re.search(r"\.md$", path)
    if oR:
        mkd=open(path, "r").read()
        return render_template("default.html", mkd=mkd, STATIC_PATH=STATIC_PATH)
    return abort(404)

def run():
    app.run(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    run()