import time
import json
import requests
from random import randint
import socket

portRange = range(5000, 6000)

def generate_node_id():
    millis = int(round(time.time() * 1000))
    node_id = millis + randint(800000000000, 900000000000)
    return node_id


# This method is used to register the service in the service registry
def register_service(name, port, node_id):
    print(f"registered service, {name}, {port}")

    # derigster unnecessary services first
    ids = get_list_of_node_ids(port)
    print("found ids:", ids)
    url = "http://localhost:8500/v1/agent/service/deregister/"
    for i in ids:
        requests.put(url + str(i))

    url = "http://localhost:8500/v1/agent/service/register?replace-existing-checks=true"
    data = {
        "Name": name,
        "ID": str(node_id),
        "port": port,
        "check": {
            "name": "Check Counter health %s" % port,
            "tcp": "localhost:%s" % port,
            "interval": "10s",
            "timeout": "1s"
        }
    }
    put_request = requests.put(url, json=data)
    return put_request.status_code

def check_node_available(port):
    # url = 'http://localhost:%s/' % port
    # post_response = requests.post(url)
    # if 200 == post_response:
    #     return 200
    # return 404
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        res = sock.connect_ex(('localhost', port))
        if res == 0:
            return True
        else:
            return False

def get_free_port_and_node_name():
    used_ports = []
    ports = get_ports_of_nodes()
    for n, p in ports.items():
        if check_node_available(p):
            used_ports.append(p)
    # get first unused port in port range
    p = list(filter(lambda x: x not in used_ports, portRange))
    if len(p) < 1:
        print("error: no port free in range.")
        exit(1)
    else: 
        p = p[0]
    return p, "node" + str(p-5000)

def check_health_of_the_service(service):
    print('Checking health of the %s' % service)

    # url = 'http://localhost:8500/v1/agent/health/service/name/%s' % service
    # response = requests.get(url)
    # response_content = json.loads(response.text)
    # aggregated_state = response_content[0]['AggregatedStatus']
    # service_status = aggregated_state
    # if response.status_code == 503 and aggregated_state == 'critical':
    #     service_status = 'crashed'
    # print('Service status: %s' % service_status)
    # return service_status

    return service in get_ports_of_nodes().keys()



# get ports of all the registered nodes from the service registry
def get_ports_of_nodes():
    ports_dict = {}
    response = requests.get('http://127.0.0.1:8500/v1/agent/services')
    nodes = json.loads(response.text)
    for each_service in nodes:
        service = nodes[each_service]['Service']
        status = nodes[each_service]['Port']
        key = service
        value = status
        if check_node_available(value):
            ports_dict[key] = value
    return ports_dict

def get_list_of_node_ids(port):
    id_list = []
    response = requests.get('http://127.0.0.1:8500/v1/agent/services')
    nodes = json.loads(response.text)
    for each_service in nodes:
        id = nodes[each_service]['ID']
        if nodes[each_service]['Port'] == port:
            id_list.append(id)

    return id_list

def get_higher_nodes(node_details, node_id):
    higher_node_array = []
    for each in node_details:
        if each['node_id'] > node_id:
            higher_node_array.append(each['port'])
    return higher_node_array


# this method is used to send the higher node id to the proxy
def elect_higher_nodes(higher_nodes_array, node_id):
    status_code_array = []
    for each_port in higher_nodes_array:
        url = 'http://localhost:%s/proxy' % each_port
        data = {
            "node_id": node_id
        }
        post_response = requests.post(url, json=data)
        status_code_array.append(post_response.status_code)
    if 200 in status_code_array:
        return 200


# this method returns if the cluster is ready for the election
def ready_for_election(ports_of_all_nodes, self_election, self_coordinator):
    coordinator_array = []
    election_array = []
    node_details = get_details(ports_of_all_nodes)

    for each_node in node_details:
        coordinator_array.append(each_node['coordinator'])
        election_array.append(each_node['election'])
    coordinator_array.append(self_coordinator)
    election_array.append(self_election)

    if True in election_array or True in coordinator_array:
        return False
    else:
        return True


# this method is used to get the details of all the nodes by syncing with each node by calling each nodes' API.
def get_details(ports_of_all_nodes):
    node_details = []
    for each_node in ports_of_all_nodes:
        if check_node_available(ports_of_all_nodes[each_node]):
            url = 'http://localhost:%s/nodeDetails' % ports_of_all_nodes[each_node]
            data = requests.get(url)
            node_details.append(data.json())
    return node_details


# this method is used to announce that it is the master to the other nodes.
def announce(coordinator):
    all_nodes = get_ports_of_nodes()
    data = {
        'coordinator': coordinator
    }
    for each_node in all_nodes:
        url = 'http://localhost:%s/announce' % all_nodes[each_node]
        print(url)
        requests.post(url, json=data)
