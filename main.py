import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()

from database.database import engine, Base

from models.user import User  # noqa: F401

from routers.login import router as login_router
from routers.signup import router as signup_router
from routers.ecg import router as ecg_router
from routers.ecghistory import router as ecg_history_router
from routers.ecganalysisresult import router as ecg_result_router


app = FastAPI(title="ECG App")

templates = Jinja2Templates(directory="templates")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "change-me-in-production")
)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    user_name = request.session.get("user_name")
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "user_name": user_name})


app.include_router(login_router)
app.include_router(signup_router)
app.include_router(ecg_router)
app.include_router(ecg_history_router)
app.include_router(ecg_result_router)
