from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
import numpy as np
import requests
import json
import zmq

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# A welcome message to test our server
@app.route('/')
@cross_origin()
def index():
    r = requests.get('https://api-randomizer.herokuapp.com/bit?n=4')
    print('Started server')
    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: %s" % message)

        #  Do some 'work'
        time.sleep(1)

        #  Send reply back to client
        socket.send(b"World")
    data = json.loads(r.text)
    print(data)
    return jsonify(data)

if __name__ == '__main__':

    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
