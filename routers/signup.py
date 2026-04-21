from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session


from database.database import get_db
from models.user import User
from database.security import hash_password
router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/signup", response_class=HTMLResponse, name="signup")
def singup(request: Request):
    return templates.TemplateResponse(request, "signup.html", {})

@router.post("/signup")
def signup_user(
    request: Request,
    full_name: str = Form(...),
    specialty: str = Form(None),
    institution: str = Form(None),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request, "signup.html",
            {"error": "Passwords do not match"},
            status_code=400
        )

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        specialty=specialty,
        institution=institution
    )

    db.add(user)
    db.commit()
    request.session["user_id"] = str(user.id)
    request.session["user_name"] = user.full_name
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="user_name",
        value=full_name,
        httponly=False   # frontend needs it
    )
    return response

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
