from fastapi import APIRouter, Request, Depends,HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database.database import get_db
from models.ecg import ECGDatabase
import os 
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/ecghistory", response_class=HTMLResponse)
def ecg_history(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login", status_code=303)

    ecgs = (
        db.query(ECGDatabase)
        .filter(ECGDatabase.user_id == user_id)
        .order_by(ECGDatabase.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request, "ecghistory.html",
        {
            "user_name": request.session.get("user_name"),
            "ecgs": ecgs,
        },
    )


@router.delete("/ecg/{ecg_id}")
async def delete_ecg(ecg_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    ecg = db.query(ECGDatabase).filter(
        ECGDatabase.id == ecg_id,
        ECGDatabase.user_id == user_id
    ).first()

    if not ecg:
        raise HTTPException(status_code=404, detail="ECG not found")

    if ecg.ecg_image_path and os.path.exists(ecg.ecg_image_path):
        try:
            os.remove(ecg.ecg_image_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

    db.delete(ecg)
    db.commit()
    ecgs = (
        db.query(ECGDatabase)
        .filter(ECGDatabase.user_id == user_id)
        .order_by(ECGDatabase.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        request, "ecghistory.html",
        {
            "user_name": request.session.get("user_name"),
            "ecgs": ecgs,
        },
    )