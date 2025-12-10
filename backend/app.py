from routes.users import user_router
from routes.categories import category_router
from routes.budgets import budget_router
from routes.expenses import expense_router
from routes.analytics import analytics_router
from routes.incomes import income_router
from routes.websocket import websocket_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from middleware.auth import auth_middleware
from utils.utils import create_default_budgets
import os


app = FastAPI()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.state.UPLOAD_DIR = UPLOAD_DIR

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router)
app.include_router(category_router)
app.include_router(budget_router)
app.include_router(expense_router)
app.include_router(analytics_router)
app.include_router(income_router)
app.include_router(websocket_router)

app.middleware("http")(auth_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # URLs to allow
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE all allowed
    allow_headers=["*"],  # All headers allowed
)


@app.on_event("startup")
def startup_event():
    create_default_budgets()


@app.get("/")
async def home():
    return "API connection Successful. Welcome to PFT"
