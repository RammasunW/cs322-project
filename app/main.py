from fastapi import FastAPI

from .database import Base, engine
from .routers import test_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant App")

app.include_router(test_router.router)


@app.get("/")
def home():
    return {"message": "Server is running!"}
