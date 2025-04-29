# backend/main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from workflow import run_workflow  # Import the workflow
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - for development purposes only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    text: str

@app.post("/process")
async def process_query(request: QueryRequest):
    try:
        result = run_workflow(request.text)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
