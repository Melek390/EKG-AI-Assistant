from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User
from database.security import verify_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse, name="login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {})


@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1️⃣ Find user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return templates.TemplateResponse(
            request, "login.html",
            {"error": "Invalid email or password"},
            status_code=400
        )

    # 2️⃣ Verify password
    if not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request, "login.html",
            {"error": "Invalid email or password"},
            status_code=400
        )

    # 3️⃣ Store session
    request.session["user_id"] = str(user.id)
    request.session["user_name"] = user.full_name

    # 4️⃣ Redirect home
    return RedirectResponse(url="/", status_code=303)
