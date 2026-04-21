from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dependencies.auth import require_login
from models.ecg import ECGDatabase
from database.database import get_db
import os
import uuid

router = APIRouter()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "assets/uploads/ecg"

@router.get("/ecg", response_class=HTMLResponse, name="ecg")
def ecg(request: Request,auth=Depends(require_login)):
    if auth:
        return auth 
    user_name = request.session.get("user_name")
    return templates.TemplateResponse(
        "ecg.html",
        {"request": request,
         "user_name": user_name}
    )
@router.post("/ecg")
async def submit_ecg(
    request: Request,
    age: int = Form(None),
    history: str = Form(None),
    symptoms: str = Form(None),
    ecg_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 🔐 Ensure user is logged in
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    # 📁 Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 🖼 Save image with unique name
    file_ext = ecg_image.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await ecg_image.read())

    # 💾 Save to database
    ecg_entry = ECGDatabase(
        age=age,
        history=history,
        symptoms=symptoms,
        ecg_image_path=file_path,
        user_id=user_id,
    )

    db.add(ecg_entry)
    db.commit()
    db.refresh(ecg_entry)

    # ✅ Redirect after success
    return RedirectResponse(url=f"/ecg/{ecg_entry.id}/result", status_code=303)