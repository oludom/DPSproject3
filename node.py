from flask import Flask, request, jsonify, render_template
import flask
from bully import Bully
import threading
import time
import random
import sys
import requests
from connector import PORT

import socket

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
# print(hostname, local_ip)

app = Flask(__name__)

b = Bully()

@app.route('/')
def index():
    return jsonify({'response': 'OK'}), 200

@app.route('/election')
def electionMessage():
    b.receiveElectionMessage(flask.request.remote_addr)
    return jsonify({'response': 'OK'}), 200

@app.route('/answer')
def answer():
    b.answer()
    return jsonify({'response': 'OK'}), 200

@app.route('/coordinator')
def coordinator():
    b.coordinator(flask.request.remote_addr)
    return jsonify({'response': 'OK'}), 200

@app.route('/details')
def details():
    return jsonify(b.getDetails())

@app.route('/ui')
def ui():
    allNodes = b.getNodeList()
    allNodes.sort(key=lambda x: bytes(map(int, x.split('.'))))
    nodeList = []
    messageTotal = 0
    for n in allNodes:
        res = requests.get('http://' + n + ':' + str(PORT) + '/details')
        j = res.json()
        nodeList.append(j)
        messageTotal += j['totalMessageCount']
    return render_template("dashboard.html", nodeList=nodeList, messageTotal=messageTotal)

# No node spends idle time, they always checks if the master node is alive in each 60 seconds.
def check_coordinator_health():
    threading.Timer(30, check_coordinator_health).start()
    if not b._coordinator:
        if not b.checkCoordinator():
            b.sendElectionMessage()
    else: 
        print("I am coordinator and alive.", flush=True)
    return

def init():
    b.join()

timer_thread1 = threading.Timer(random.randint(20, 30), init)
timer_thread1.start()
timer_thread2 = threading.Timer(50, check_coordinator_health)
timer_thread2.start()

if __name__ == '__main__':
    app.run(host=local_ip, port=5000)
