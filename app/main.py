from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

