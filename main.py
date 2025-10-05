from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from redis import RedisError
from planets.routes.mars import router as planets_router
from ai.routes.gemeni import router as gemeni_router
from planets.config.redis_config import r, test_redis_connection


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


app = FastAPI(title="Mars Tiles API", lifespan=lifespan)
app.include_router(planets_router, prefix="/api")
app.include_router(gemeni_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "*"  
    ],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
    expose_headers=["X-Cache", "Content-Type"],
    max_age=3600,
)
