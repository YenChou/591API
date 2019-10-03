import flask
from flask_restful import Api
from resource.resource_elastic_test import data
app = flask.Flask(__name__)
app.config["DEBUG"] = True

api = Api(app)


api.add_resource(data,"/houses",endpoint='houses')

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    status_code = 500
    if type(error).__name__ == "NotFound":
        status_code = 404
    elif type(error).__name__ == "TypeError":
        status_code = 500
    return {
        'code': status_code,
        'msg': type(error).__name__
    }

@app.route("/",methods = ['GET'])
def home():
    return "<h1>API For 591租屋網</h1>"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, use_reloader=False)
