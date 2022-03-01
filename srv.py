import connexion
from flask import Flask, render_template
from flask_cors import CORS, cross_origin
from swagger_ui_bundle import swagger_ui_3_path

# add CORS headers
def set_cors_headers_on_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-Requested-With, content-type, Origin, Accept'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, PUT, GET, POST'

    return response
    
# create the application instance 
options = {'swagger_path': swagger_ui_3_path}
app = connexion.App(__name__, specification_dir='./', options=options)
CORS(app.app)

# read swagger.json files to configure endpoints
app.add_api('OADefs/example.json')

app.app.after_request(set_cors_headers_on_response)

# create URL route in our app for /

@app.route('/')
@cross_origin()
def home():
    """
    Responds to localhost:8000/
    :return: the rendered template 'home.html'
    """

    return render_template('home.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)