from flask import g, Flask, request, send_file, redirect, session, jsonify, abort
from flask import render_template as render_template_default
import os
import re

from flask_caching import Cache
from flask import Response
from jinja2 import Template, FunctionLoader, Environment, BaseLoader
from flask import Flask
import mimetypes
import datetime
from flaskext.markdown import Markdown
import zipfile
import getopt
import sys
import pkgutil
from os import walk
import re
from functools import reduce
import markdown as md
from markdown import (
    blockprocessors,
    Extension,
    preprocessors,
)
import pydotenv
env = pydotenv.Environment()

# NOTE: Переменные, Приложение flask(app)
app = Flask(__name__)
cache = Cache(app)

config = {}
app.config.from_mapping(config)

MD_PATH = "./md"
try:
    iI = sys.argv.index("-d")
    MD_PATH = sys.argv[iI+1]
    del sys.argv[iI:iI+2]
except:
    pass

MD_PATH=env.get('MD_PATH', MD_PATH)
__DEBUG__ = env.get('__DEBUG__', False)
STATIC_PATH = "/static"
if (__DEBUG__):
    STATIC_PATH = "/zip/static"

oMarkdown = Markdown(app)

def readfile(sFilePath):
    if (__DEBUG__):
        return open(sFilePath, 'rb').read()
    elif getattr(sys, 'frozen', False):
        print(sFilePath)
        return pkgutil.get_data('main', sFilePath )
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
    print("[>]", path)
    oR = re.search(r"\.md$", path)
    if oR:
        mkdtext=open(path, "r").read()
        mkd = md.Markdown()
        mdhtml=mkd.convert(mkdtext)
        return render_template("default.html", mdhtml=mdhtml, STATIC_PATH=STATIC_PATH)
    else:
        if os.path.isfile(path):
            oR = Response(open(path, "rb").read(), mimetype=mimetypes.guess_type(path)[0])
            oR.headers['Cache-Control'] = 'max-age=60480000, stale-if-error=8640000, must-revalidate'
            return oR
    return abort(404)

@cache.cached(timeout=50, key_prefix='markdown_files_menu')
def fnPrepareMarkdownFilesListMenu(sDir=MD_PATH):
    aExtFiles = []
    for (dirpath, dirnames, filenames) in walk(sDir):
        for sF in filenames:
            sP = os.path.join(MD_PATH, sF)
            sFC = open(sP).read()
            m = re.search(r"# ([^\n]*)", sFC) 
            sTitle = sP
            if (m):
                sTitle = m.group(1)
            aExtFiles.append([sTitle, sP, sF])
        for sD in dirnames:
            print([sD])
            aExtFiles.extend(fnPrepareMarkdownFilesListMenu(sD))        
        break

    return aExtFiles

@cache.cached(timeout=50, key_prefix='markdown_file_menu')
def fnPrepareMarkdownMenu(sFile):
    aMenu = []
    sFC = open(sFile).read()
    iI=0
    oM = re.findall(r"(#+) ([^\n]*)", sFC) 
    if (oM):
        for aItem in oM:
            iI += 1
            aMenu.append([
                '#a'+str(iI),
                len(aItem[0]),
                aItem[1]
            ])
    return aMenu

@app.route("/", methods=['GET', 'POST'])
def index():
    path = os.path.join(MD_PATH, "index.md")
    # if os.path.isfile(path):
    #     mkdtext=open(path, "r").read()
    #     mkd = md.Markdown()
    #     mdhtml=mkd.convert(mkdtext)
    #     return render_template("default.html", mdhtml=mdhtml, STATIC_PATH=STATIC_PATH)
    # else:
    
    sFile = ""
    if "file" in request.args:
        sFile = request.args["file"]

    aLeftMenu=fnPrepareMarkdownFilesListMenu()
    aFileMenu=[]
    sFileMarkdown=""

    if sFile:
        aFileMenu=fnPrepareMarkdownMenu(sFile)
        mkdtext=open(path, "r").read()
        mkd = md.Markdown()
        mdhtml=mkd.convert(mkdtext)
        sFileMarkdown = mdhtml

        global iI
        iI = 0
        def fnReducer(m): 
            global iI
            iI += 1
            return '<a name="a'+ str(iI) +'"></a>' + m.group(0)
        
        # sFileMarkdown = reduce(fnReducer, re.findall(r"<h\d+", sFileMarkdown), sFileMarkdown)
        sFileMarkdown = re.sub(r"<h\d+", fnReducer, sFileMarkdown)

    return render_template(
        "index.html", 
        STATIC_PATH=STATIC_PATH, 
        aLeftMenu=aLeftMenu,
        aFileMenu=aFileMenu,
        sFileMarkdown=sFileMarkdown
    )

# def run():
#     app.run(host='0.0.0.0')

# if __name__ == "__main__":
#     run()