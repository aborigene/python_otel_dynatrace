from fastapi import FastAPI, Request
import time
import mysql.connector
from mysql.connector import Error

from random import seed
from random import randint

import json

from opentelemetry import trace as OpenTelemetry
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
import os

merged = dict()
for name in ["dt_metadata_e617c525669e072eebe3d0f08212e8f2.json", "/var/lib/dynatrace/enrichment/dt_metadata.json"]:
    try:
        data = ''
        with open(name) as f:
          data = json.load(f if name.startswith("/var") else open(f.read()))
        merged.update(data)
    except:
        pass

merged.update({
    "service.name": "mensagens", 
    "service.version": "0.0.1", 
})

resource = Resource.create(merged)

tracer_provider = TracerProvider(sampler=sampling.ALWAYS_ON, resource=resource)
OpenTelemetry.set_tracer_provider(tracer_provider)

# Get OTEL environment variables
DT_ENDPOINT = os.getenv('DT_ENDPOINT')
DT_TOKEN = os.getenv('DT_TOKEN')
print(DT_TOKEN)
print(DT_ENDPOINT)

tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(
        endpoint=DT_ENDPOINT,
        headers={
          "Authorization": "Api-Token "+str(DT_TOKEN)
        },
    )))

#tracer_provider.add_span_processor(
#    BatchSpanProcessor(OTLPSpanExporter(
#        endpoint="http://localhost:14499/otlp/v1/traces"
#    )))

tracer = OpenTelemetry.get_tracer(__name__)

connection = None
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='python_test',
                                         user='root')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)
    quit()
#finally:
#    if connection.is_connected():
#        cursor.close()
#        connection.close()
#        print("MySQL connection is closed")
app = FastAPI()

seed(1)
@app.get("/mensagem")
async def root(request: Request):
    for header in request.headers:
        print(header, '->', request.headers[header])
#    print("Dynatrace tag: " + request.headers.get('x-Dynatrace'))
    cursor = connection.cursor()

    cursor.execute("select count(*) from messages;")
    value = randint(1, cursor.fetchone()[0])
    cursor.execute("select mensagem from messages where id = "+str(value)+";")
    doSomeWork()
    return {"message": cursor.fetchone()}

def doSomeWork():
    with tracer.start_as_current_span("doSomeWork") as span:
        time.sleep(10)
        print("Dormi por 10 segundos...")
