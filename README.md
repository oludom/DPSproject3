# Deciding the Coordinator in a cluster. 

This repository contains a project, which explores leader election in distributed systems. The project was done for the course Distributed and Pervasive Systems at Aarhus University. The Bully Algorithm was implemented in python and uses Flask for simple network communication and a small ui, showing the state of the network. 

To run the code, make sure the minikube is started - `$ minikube start`.

Buld and push the docker image:

`$ docker build -t accountname/dpsp3node . --no-cache --force-rm`

`$ docker push accountname/dpsp3node`


Apply the service and development:

`$ kubectl apply -f list_service.yaml`

`$ kubectl apply -f deployment.yaml`


Get names of the pods and their statuses:

`$ kubectl get pods`


Access the console logs of a specific pod:
`$ kubectl logs -f nameofthepod`
