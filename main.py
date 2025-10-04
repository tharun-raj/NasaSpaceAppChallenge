from fastapi import FastAPI
from mars.routes.mars import router as mars_router
from labels import labels
from labels.db import create_table

app = FastAPI(title="Mars Tiles API")

@app.on_event("startup")
def startup_event():
    create_table()

app.include_router(mars_router, prefix="/api")
app.include_router(labels.router, prefix="/labels", tags=["Labels"])