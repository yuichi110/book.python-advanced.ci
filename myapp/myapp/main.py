from fastapi import FastAPI
from myapp.service import IndexService

app = FastAPI()


@app.get("/")
def index():
    service = IndexService()
    return service.serve()
