from fastapi import FastAPI
from . import models
from .database import engine
from .routers import stations, user, vehicles, auth, sessions, ports, payments, discount
from fastapi.middleware.cors import CORSMiddleware

"""
Main application module for the FastAPI backend
Initializes the database and sets up API routes
"""

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Charging Station API",
    description="API for managing electric vehicle charging stations",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(vehicles.router)
app.include_router(stations.router)
app.include_router(ports.router)
app.include_router(sessions.router)
app.include_router(payments.router)
app.include_router(discount.router)