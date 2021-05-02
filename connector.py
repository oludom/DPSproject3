import socket, requests, nslookup

# config
PORT = 5000

class ConnectionService():

    def __init__(self):
        self._name = socket.gethostname()
        self._ip = socket.gethostbyname(self._name)

    # returns list of nodes in cluster
    def getNodeList(self):
        n = nslookup.Nslookup().dns_lookup("headless-service.default.svc.cluster.local")
        return n.answer

    def sendElectionMessage(self, ip):
        return self.checkNodeAvailable(ip, '/election')

    def sendCoordinatorMessage(self, ip):
        return self.checkNodeAvailable(ip, '/coordinator')

    def sendAnswer(self, ip):
        self.checkNodeAvailable(ip, '/answer')

    def checkNodeAvailable(self, ip, path=''):
        try:
            res = requests.get('http://' + ip + ":" + str(PORT) + path)
            res.raise_for_status()
        except requests.exceptions.HTTPError:# as http_err:
            # print(f'HTTP error occurred: {http_err}', flush=True)
            return False
        except Exception:
            # print("Node available: FALSE", flush=True)
            return False
        
        # print("Node available: TRUE", flush=True)
        return True