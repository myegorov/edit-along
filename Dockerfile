FROM python:3

COPY . /opt/app
WORKDIR /opt/app/py

RUN pip install -r ../requirements.txt

EXPOSE 1070

CMD ["python3", "server.py", "-e", "DEV"]
