from operator import imod
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# from cardioBackend.database import engine
from cardioBackend.routers import auth, patients, readings, users

app = FastAPI()

# models.Base.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(readings.router)


@app.get("/")
def root():
    return {"Hello": "World"}


if __name__ == '__main__':
    uvicorn.run("app:app",
                host="0.0.0.0",
                port=8432,
                reload=True,
                )