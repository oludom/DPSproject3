from connector import ConnectionService
import threading
import time

class Bully:

    # def __init__(self, node_name, node_id, port_number, election=False, coordinator=False):
    #     self.node_name = node_name
    #     self.node_id = node_id
    #     self.port = port_number
    #     self.election = election
    #     self.coordinator = coordinator

    def __init__(self):
        self._connection = ConnectionService()
        self._election = False
        self._coordinator = False
        self._currentCoordinatorIp = self._connection._ip
        


    # join network
    def join(self):
        self.sendElectionMessage()

    # sent to announce election
    def sendElectionMessage(self):
        print('bully.sendElectionMessage', flush=True)
        self._election = True

        nodes = self._connection.getNodeList()
        print("nodesList:", nodes, flush=True)
        nodes.remove(self._connection._ip)
        print("nodesList:", nodes, flush=True)
        # send to higher numbered nodes
        higher = list(filter(lambda x: self.compareIpHigher(self._connection._ip, x) , nodes)) 
        # if no higher nodes, you are leader
        print("higher:", higher, flush=True)
        if len(higher) < 1: 
            self._announceCoordinator(nodes)
        else:
            # elect higher nodes
            for i in range(len(higher)):
                self._connection.sendElectionMessage(higher[i])
            # set timer for checking answers
            threading.Timer(3, self._electionTimeout).start()
    
    def receiveElectionMessage(self, ip):
        if self._coordinator:
            self._announceCoordinator([ip])
            return
        print('bully.receiveElectionMessage', flush=True)
        print("remote ip: ", ip, flush=True)
        if self.compareIpHigher(self._connection._ip, ip):
            # other is leader, wait for victory
            self._election = False
        else:
            self.sendElectionMessage()
            self._connection.sendAnswer(ip)
    
    # answers election message (alive)
    def answer(self):
        if self._election:
            self._election= False


    # coordinator message (victory)
    def coordinator(self, ip):
        print('bully.coordinator', flush=True)
        self._coordinator = False
        self._currentCoordinatorIp = ip
        self._election = False

    def compareIpHigher(self, one, two):
        one = bytes(map(int, one.split('.')))
        two = bytes(map(int, two.split('.')))
        return one < two

    def checkCoordinator(self):
        print('bully.checkCoordinator', flush=True)
        return self._connection.checkNodeAvailable(self._currentCoordinatorIp)

    def _announceCoordinator(self, nodes):
        print("bully.announceCoordinator: ", nodes)
        self._election = False
        self._coordinator = True
        # announce coordinator
        for i in range(len(nodes)):
            self._connection.sendCoordinatorMessage(nodes[i])

    def _electionTimeout(self):
        if self._election:
            nodes = self._connection.getNodeList()
            nodes.remove(self._connection._ip)
            self._announceCoordinator(nodes)