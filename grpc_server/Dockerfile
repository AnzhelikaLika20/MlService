FROM python:3.11

WORKDIR /grpc_server

COPY . .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "server.py"]
