from fastapi import FastAPI
from . import models
from .database import engine
from .routers import stations, user, vehicles, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(stations.router)
app.include_router(vehicles.router)