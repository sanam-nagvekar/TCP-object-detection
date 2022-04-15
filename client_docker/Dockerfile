# Base image
FROM python:3

RUN mkdir -p /client

COPY ../client.py .
COPY ../requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python3", "client.py" ]