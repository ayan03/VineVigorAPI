from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

app = FlaskAPI(__name__)

@app.route('/', methods = ['GET', 'POST'])
def test():
    if request.method == 'POST':
        print("Handling POST request")
        body = {'POST' : 'POST data'}
        return body, status.HTTP_200_OK
    else:
        print("Handling GET request")
        body = {'GET' : 'GET data'}
        return body, status.HTTP_200_OK

if __name__ == "__main__":
    app.run(debug=True)