from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    return {"message": "DevOps Sample App Running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}