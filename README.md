# Deciding the Coordinator in a cluster. 

1. As the reservice registry, this implementation uses Consul. Please read more https://www.consul.io/. You can follow the these steps to install Consul. https://learn.hashicorp.com/consul/getting-started/install

2. Make sure to verify by verifying the version of consul. 
```
consul --version
```

3. Start the service registry as below. 
```
consul agent -dev
```

4. Since this implmenetation each node runs in the same code base, we need to provide port number and the node name via command line arguments. This cluster has 4 nodes with the same code base. You need to run the each node in a new terminal. 

Node1
```
 python test.py 5001 node1
```

Node2
```
 python test2.py 5002 node2
```

Node3
```
 python test3.py 5003 node3
```

Node4
```
 python test4.py 5004 node4
```

Once the master node is decided, you can see the similar outputs in the nodes as below. 

Master node
```
 * Serving Flask app "test2" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
Starting election in: node2
higher node array []
http://localhost:5001/announce
http://localhost:5004/announce
http://localhost:5003/announce
http://localhost:5002/announce
Coordinator is node2 
Coordinator is : node2
**********End of election**********************

```

Other nodes
```
(BullyAlgorithmImplemetation) isuruuy@Isurus-MacBook-Pro BullyAlgorithmImplemetation % python test.py 5001 node1
 * Serving Flask app "test" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
timeouting in 8 seconds
Starting election in: node1
higher node array [5003, 5002]
Coordinator is node2 

```

```
(BullyAlgorithmImplemetation) isuruuy@Isurus-MacBook-Pro BullyAlgorithmImplemetation % python test3.py 5003 node3
 * Serving Flask app "test3" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
Starting election in: node3
higher node array [5002]
Coordinator is node2 
```



program flow:

import ...
create app()
get_free_port_and_node_name()
create logger()
generate_node_id()
create Bully(name, id, port) 

register_service(name, port, id)

create routes()
  /response
    -> runs new Thread init
      if own node id > incoming request node id

  /announce
    -> receives coordinator announcement
      saves it in bully object
  
  /proxy
    -> counts incoming requests during election and will only forward one call to own response api

  / 
    -> node health check, responds with 200


main: 
  app.run()

after 15s:
  init()
    get_ports_of_nodes()
    get_details() of all nodes
    ready_for_election()
    get_higher_nodes()
      announce()
        if no higher nodes
    or
      elect_higher_nodes()
        if there are higher nodes

    
after 20s: 
  check_coordinator_health()