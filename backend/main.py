#!/usr/bin/python3
"""Module that starts the FastAPI app"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", port=8000, reload=True)
