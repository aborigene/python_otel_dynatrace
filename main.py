from fastapi import FastAPI
import requests 

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

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello this is a test..."}

@app.get("/hello")
async def root():
    r = requests.get('http://127.0.0.1:8001/mensagem')
    print(r.text)
    return {"message": "Hello: "+r.text}
