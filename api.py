from flask import Flask, request
from utils import Reference


app = Flask(__name__)
ref = Reference()


@app.route('/jjap-like/<path:doi>')
def get_jjap(doi):
    return ref(doi).jjap_like()


@app.route('/jjap-fullname/<path:doi>')
def get_jjap_fullname(doi):
    return ref(doi).jjap_like(False)


@app.route('/bibtex/<path:doi>')
def get_bibtex(doi):
    return ref(doi).bibtex()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001, threaded=True)

