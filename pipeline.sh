docker build -t eld3rb3rry/dpsp3node .
docker push eld3rb3rry/dpsp3node
kubectl delete -f deployment.yaml
kubectl apply -f deployment.yaml
watch kubectl get pods