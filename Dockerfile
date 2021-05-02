FROM python:3.7

RUN mkdir /app
RUN mkdir /app/logs
WORKDIR /app
ADD node.py /app/node.py
ADD connector.py /app/connector.py
ADD bully.py /app/bully.py
ADD static/style.css /app/static/style.css
ADD templates/dashboard.html /app/templates/dashboard.html
RUN pip install flask requests nslookup

CMD ["python", "/app/node.py"]