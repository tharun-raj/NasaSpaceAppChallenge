from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from redis import RedisError
from planets.routes.planets import router as planets_router
from planets.routes.health import router as health_router
from ai.routes.gemeni import router as gemeni_router
from planets.config.redis_config import r, test_redis_connection
from labels import labels
from forum.forum import router as forum_router
from user.user import router as user_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        test_redis_connection()
        print("Connected to Redis")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        raise e

    yield 

    try:
        r.close()
        print("Redis connection closed.")
    except RedisError as e:
        print(f"Error closing Redis connection: {e}")


app = FastAPI(title="Planet Tiles API", lifespan=lifespan)
app.include_router(planets_router, prefix="/api")
app.include_router(gemeni_router, prefix="/api")
app.include_router(labels.router, prefix="/labels", tags=["Labels"])
app.include_router(health_router)
app.include_router(forum_router, prefix="/forum")
app.include_router(user_router, prefix="/user")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"  
    ],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
    expose_headers=["X-Cache", "Content-Type"],
    max_age=3600,
)
