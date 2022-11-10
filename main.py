from flask import Flask, render_template, request, make_response, jsonify, redirect, url_for, send_file
from flask_cors import CORS
from wocelconnectors.algo.connectors import factory as connectors_factory
import tempfile
import pm4py


app = Flask(__name__)
CORS(app, expose_headers=["x-suggested-filename"])


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
    pm4py.write_ocel(ocel, temp_file.name)

    resp = send_file(temp_file.name,
                       mimetype="text/json",  # use appropriate type based on file
                       as_attachment=True,
                       conditional=False)
    resp.headers["x-suggested-filename"] = variant+".json"

    return resp


def main():
    app.run(host='0.0.0.0', threaded=True)


if __name__ == "__main__":
    main()
