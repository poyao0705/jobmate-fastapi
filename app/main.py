from fastapi import FastAPI
from app.routers import resumes
from app.db.database import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(resumes.router)


@app.get("/")
async def main():
    return {"message": "Hello from jobmate-fastapi!"}
