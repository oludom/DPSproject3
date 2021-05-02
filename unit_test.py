import pytest
import requests
from connector import ConnectionService
import threading
import time

PORT = 5000

def getNodeList():
        return [_service._ip,"192.168.1.21","192.168.1.17","192.168.1.22"]

_service = ConnectionService()
print(_service._ip,flush=True)
print(_service._name,flush=True)
_nodes = getNodeList()
_election = False
_coordinator = False


def answer():
    global _election
    if (_election):
        _election = False

def compareIpHigher(one, two):
        one = bytes(map(int, one.split('.')))
        two = bytes(map(int, two.split('.')))
        return one < two

def checkNodeAvailable(ip, path=''):

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

def _announceCoordinator( nodes):
    global _coordinator
    global _election
    global _service

    print("bully.announceCoordinator: ", nodes)
    _election = False
    _coordinator = True
    # announce coordinator
    for i in range(len(nodes)):
        _service.sendCoordinatorMessage(nodes[i])

def _electionTimeout():
    if _election:
        _nodes.remove(_service._ip)
        _announceCoordinator(_nodes)

def _sendElectionMessage():
    global _service
    global _election
    global _nodes
    global _coordinator
    
    print('sendElectionMessage', flush=True)
    
    _election = True

    _nodes.remove(_service._ip)
    # print("nodesList:", nodes, flush=True)
    # send to higher numbered nodes
    higher = list(filter(lambda x: compareIpHigher(_service._ip, x) , _nodes)) 
    # if no higher nodes, you are leader
    higher.sort(key=lambda x: bytes(map(int, x.split('.'))))

    print("higher:", higher, flush=True)

    if len(higher) < 1: 
        _announceCoordinator(_nodes)
    else:
        # elect highest node
        _service.sendElectionMessage(higher[-1])
        # set timer for checking answers
        threading.Timer(3, _electionTimeout).start()


# ------------------------ TESTS FUNCTIONS BELOW ------------------------ # 

def test_election_timeout():
    global _coordinator
    global _election
    global _nodes
    _election = True
    _electionTimeout()
    assert _coordinator == True
    _election = False
    _nodes.append(_service._ip)

def test_compareIpHigher():
    ip_1 = "192.168.1.20"
    ip_2 = "192.168.1.21"

    # expected output:
    # True if ip_2 > ip_1
    assert compareIpHigher(ip_1,ip_2) == True

    # expected output:
    # False if ip_1 > ip_2
    assert compareIpHigher(ip_2,ip_1) == False

def test_checkNodeAvailable_service_up():
    # expected output
    # True if Flask server is up and running 
    assert _service.checkNodeAvailable(_service._ip) == True

def test_answer():
    answer()
    assert _election == False
    
def test_sendElectionMessage():
    global _nodes
    _sendElectionMessage()
    # b._election should be  True as election has been started
    assert _election == True

    _nodes.append(_service._ip)

def test__checkNodeAvailable_service_down():
    global _service
    _service = None

    # expected output
    # Exception raised if there is no service manager
    with pytest.raises(Exception):
        _service.checkNodeAvailable(_service._ip)









