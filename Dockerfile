FROM python:3.7

RUN mkdir /app
RUN mkdir /app/logs
WORKDIR /app
ADD node.py /app/node.py
ADD consul_connector.py /app/consul_connector.py
ADD bully.py /app/bully.py
RUN pip install flask requests nslookup

CMD ["python", "/app/node.py"]