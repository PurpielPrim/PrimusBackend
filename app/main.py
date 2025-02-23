from fastapi import FastAPI
from . import models
from .database import engine
from .routers import stations, user, vehicles, auth, sessions, ports, payments
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#uvicorn app.main:app --reload

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(vehicles.router)
app.include_router(stations.router)
app.include_router(ports.router)
app.include_router(sessions.router)
app.include_router(payments.router)
