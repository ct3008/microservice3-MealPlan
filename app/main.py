from fastapi import Depends, FastAPI, Request
import uvicorn
import logging
import time
from fastapi.middleware.cors import CORSMiddleware
import json

from app.routers import mealplan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify the origin here, e.g., ["http://localhost:4200"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Middleware to log requests before and after
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    # Log before the request is processed
    start_time = time.time()

    # Call the next process in the pipeline
    response = await call_next(request)

    # Log after the request is processed
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} | Time: {process_time:.4f}s")

    return response


app.include_router(mealplan.router)


@app.get("/")
async def root():
    return {"message": "Hello mealplan Applications!"}

with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)


