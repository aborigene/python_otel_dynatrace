### What is this?
Simple program that has two endpoints. First endpoint calls the second one. Second one connects to MySQL and gets a ramdom message, sent back to the first service and then back to the user.

### How to run this?
1. Install dependencies: ```pip install opentelemetry-instrumentation opentelemetry-sdk opentelemetry-exporter-otlp-proto-http  opentelemetry-instrumentation-fastapi```
2. On a terminal bring up the first service: ```opentelemetry-instrument /usr/local/bin/uvicorn main:app --reload --port 8000 --workers=1```
3. On a terminal bring up the first service: ```opentelemetry-instrument /usr/local/bin/uvicorn mensagem:app --reload --port 8001 --workers=1```
4. Bring up mysql, and load the sql file from this repo.
5. Send requests to the first service, a ramdom message will be sent back to the client that made the request.