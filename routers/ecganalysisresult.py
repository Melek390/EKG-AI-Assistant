from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import logging
from requests.exceptions import ConnectionError, Timeout, RequestException

from database.database import get_db
from models.ecg import ECGDatabase
from LMMintegration.ecgassistant import generate_ecg_interpretation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/ecg/{ecg_id}/result", response_class=HTMLResponse)
def ecg_analysis_result(
    ecg_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # 🔒 Auth check
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    # Get ECG record
    ecg = db.query(ECGDatabase).filter(
        ECGDatabase.id == ecg_id,
        ECGDatabase.user_id == user_id
    ).first()

    if not ecg:
        return RedirectResponse("/ecghistory", status_code=303)

    # Generate interpretation with error handling
    interpretation = None
    error_message = None
    
    try:
        interpretation = generate_ecg_interpretation(
            image_path=ecg.ecg_image_path,
            age=ecg.age,
            history=ecg.history,
            symptoms=ecg.symptoms
        )
        logger.info(f"Successfully generated ECG interpretation for ID: {ecg_id}")
        
    except ConnectionError as e:
        error_message = "Network connection error. Please check your internet connection and try again."
        logger.error(f"Connection error for ECG {ecg_id}: {str(e)}")
        
    except Timeout as e:
        error_message = "Request timeout. The AI service is taking too long to respond. Please try again."
        logger.error(f"Timeout error for ECG {ecg_id}: {str(e)}")
        
    except RequestException as e:
        error_message = "Unable to connect to the AI service. Please try again later."
        logger.error(f"Request error for ECG {ecg_id}: {str(e)}")
        
    except Exception as e:
        error_message = "An unexpected error occurred during analysis. Please try again."
        logger.error(f"Unexpected error for ECG {ecg_id}: {str(e)}")

    # If interpretation failed, provide fallback
    if not interpretation:
        interpretation = {
            "error": True,
            "message": error_message or "Analysis could not be completed",
            "fallback_info": {
                "patient_age": ecg.age,
                "medical_history": ecg.history,
                "symptoms": ecg.symptoms,
                "recommendation": "Please consult with a healthcare professional for proper ECG interpretation."
            }
        }

    return templates.TemplateResponse(
        "ecganalysisresult.html",
        {
            "request": request,
            "user_name": request.session.get("user_name"),
            "ecg": ecg,
            "interpretation": interpretation,
            "error_message": error_message
        }
    )