from flask import Flask, render_template, request, make_response, jsonify, redirect, url_for, send_file
from flask_cors import CORS
from wocelconnectors.algo.connectors import factory as connectors_factory
import tempfile
import pm4py
import webbrowser
from threading import Timer
from random import randrange
import socket
from contextlib import closing
import requests
import setuptools
import win32com


app = Flask(__name__)
CORS(app, expose_headers=["x-suggested-filename"])



class Globals:
    PORT = 5000


@app.route("/extractCsv")
def extractCsv():
    variant = request.args.get("variant")

    parameters = {}
    for arg in request.args:
        parameters[arg] = request.args.get(arg)

    dataframe = connectors_factory.apply(variant, parameters)
    temp_file = tempfile.NamedTemporaryFile(suffix=".csv")
    temp_file.close()
    dataframe.to_csv(temp_file.name, index=False)

    resp = send_file(temp_file.name,
                       mimetype="text/plain",  # use appropriate type based on file
                       as_attachment=True,
                       conditional=False)
    resp.headers["x-suggested-filename"] = variant+".csv"

    return resp


@app.route("/extractOcel")
def extractOcel():
    variant = request.args.get("variant")

    parameters = {}
    for arg in request.args:
        parameters[arg] = request.args.get(arg)

    dataframe = connectors_factory.apply(variant, parameters)

    ocel = None
    if variant == "chrome_history":
        ocel = pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "complete_url", "url_wo_parameters", "domain"])
    elif variant == "firefox_history":
        ocel = pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "complete_url", "url_wo_parameters", "domain"])
    elif variant == "github_repo":
        ocel = pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "org:resource", "case:repo"])
    elif variant == "outlook_calendar":
        ocel = pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["case:concept:name", "case:subject"])
    elif variant == "outlook_mail_extractor":
        ocel = pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["org:resource", "recipients", "topic"])
    elif variant == "windows_events":
        ocel = pm4py.convert_log_to_ocel(dataframe, "concept:name", "time:timestamp", ["categoryString", "computerName", "eventIdentifier", "eventType", "sourceName", "user"])

    temp_file = tempfile.NamedTemporaryFile(suffix=".jsonocel")
    temp_file.close()

    ocel.relations.drop_duplicates(subset=[ocel.event_id_column, ocel.object_id_column], inplace=True)
    pm4py.write_ocel(ocel, temp_file.name)

    resp = send_file(temp_file.name,
                       mimetype="text/json",  # use appropriate type based on file
                       as_attachment=True,
                       conditional=False)
    resp.headers["x-suggested-filename"] = variant+".json"

    return resp


@app.route("/index.html")
def index():
    response = make_response(render_template('index.html'))
    return response


@app.route("/")
def welcome():
    return redirect(url_for('index'))


def open_browser():
    webbrowser.open_new("http://127.0.0.1:"+str(Globals.PORT)+"/index.html")


def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return False
        else:
            return True


def main():
    while True:
        Globals.PORT = randrange(10000, 20000)
        if check_socket("127.0.0.1", Globals.PORT):
            break
    Timer(1, open_browser).start()
    #open_browser()
    app.run(host='0.0.0.0', port=Globals.PORT, threaded=True)


if __name__ == "__main__":
    main()
