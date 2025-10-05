from fastapi import FastAPI
from mars.routes.mars import router as mars_router
from mars.routes.health import router as health_router
from labels import labels
from forum.forum import router as forum_router
from user.user import router as user_router
from db import create_table
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mars Tiles API")

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://192.168.0.124:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use ["*"] to allow all origins (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    create_table()

app.include_router(mars_router, prefix="/api")
app.include_router(labels.router, prefix="/labels", tags=["Labels"])
app.include_router(health_router)
app.include_router(forum_router, prefix="/forum")
app.include_router(user_router, prefix="/user")
