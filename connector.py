import socket, requests, nslookup

# config
PORT = 5000
CONSUL_SERVER_ADDRESS = 'http://localhost:8500'

class ConnectionService():

    def __init__(self):
        self._name = socket.gethostname()
        self._ip = socket.gethostbyname(self._name)


    # returns list of nodes in cluster
    def getNodeList(self):
        n = nslookup.Nslookup().dns_lookup("headless-service.default.svc.cluster.local")
        return n.answer
        # return ['127.0.1.1', '127.0.1.2']

    def registerNode(self, name):
        print(f"registering service, {self._name}, {self._ip}")

        # derigster unnecessary services first
        ids = self.getNodeList()
        print("found ids:", ids)
        url = CONSUL_SERVER_ADDRESS + "/v1/agent/service/deregister/"
        for i in ids:
            requests.put(url + str(i))

        url = CONSUL_SERVER_ADDRESS + "/v1/agent/service/register"
        data = {
            "Name": name,
            # "ID": str(node_id),
            "Address": self._ip,
            "Port": PORT,
            "Check": {
                "Name": "Check Counter health %s" % PORT,
                "tcp": str(self._ip) + ":%s" % PORT,
                "interval": "10s",
                "timeout": "1s",
                "DeregisterCriticalServiceAfter": "5m"
            }
        }
        put_request = requests.put(url, json=data)
        return put_request.status_code


    def sendElectionMessage(self, ip):
        return self.checkNodeAvailable(ip, '/election')

    def sendCoordinatorMessage(self, ip):
        return self.checkNodeAvailable(ip, '/coordinator')

    def sendAnswer(self, ip):
        self.checkNodeAvailable(ip, '/answer')

    def checkNodeAvailable(self, ip, path=''):
        # print('ConnectionService.checkNodeAvailable:', ip + ":" + str(PORT) + path, flush=True)
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        #     res = sock.connect_ex((ip + ":" + str(PORT) + path))
        #     if res == 0:
        #         return True
        #     else:
        #         return False
        try:
            res = requests.get('http://' + ip + ":" + str(PORT) + path)
            res.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            # print(f'HTTP error occurred: {http_err}', flush=True)
            return False
        except Exception:
            # print("Node available: FALSE", flush=True)
            return False
        
        # print("Node available: TRUE", flush=True)
        return True