
import flask
from flask import Flask, request, jsonify, render_template
import requests

local_ip = 'localhost'

app = Flask(__name__)

# @app.route('/')
# def index():
#     return jsonify({'response': 'OK'}), 200

@app.route('/details')
def details():
    return jsonify({
        'ip': '127.0.1.1',
        'name': 'dpsp3node-xxxx1',
        'leader': '127.0.1.2',
        'totalMessageCount': 10
    })

@app.route('/ui')
def ui():
    PORT = 5000
    allNodes = ['127.0.0.1', '127.0.0.1']
    nodeList = []
    messageTotal = 0
    for n in allNodes:
        res = requests.get('http://' + n + ':' + str(PORT) + '/details')
        j = res.json()
        print(j)
        nodeList.append(j)
        messageTotal += j['totalMessageCount']
    return render_template("dashboard.html", nodeList=nodeList, messageTotal=messageTotal)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
