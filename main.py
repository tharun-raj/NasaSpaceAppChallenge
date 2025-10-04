from fastapi import FastAPI
from mars.routes.mars import router as mars_router

app = FastAPI(title="Mars Tiles API")

app.include_router(mars_router, prefix="/api")