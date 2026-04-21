import os
import base64
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize OpenAI client with OpenRouter
client = OpenAI(
    api_key=os.getenv("ECG_ASSISTANT_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# Try these models in order of preference:
# Using cheaper/faster models with lower token counts
MODELS_TO_TRY = [
    "google/gemini-flash-1.5",  # Fast and cheap
    "anthropic/claude-3-haiku",  # Cheaper Claude
    "openai/gpt-4o-mini",  # Cheaper GPT-4
]

MODEL = MODELS_TO_TRY[2]  # Start with Gemini Flash


def build_ecg_prompt(age=None, history=None, symptoms=None):
    """Build the ECG interpretation prompt"""
    return f"""
You are an expert cardiologist assistant analyzing an ECG for EDUCATIONAL support purposes.



VERY IMPORTANT RULES:
- Answer STRICTLY in the SAME LANGUAGE as the user input (French ↔ English).
- Base your analysis ONLY on what you can observe in the ECG image.
- Do NOT invent measurements or findings.
- Use cautious, medical wording.
- This is an interpretation aid for medical professionals, not a final diagnosis.

========================
STEP 1 — Résumé clinique
========================
Briefly summarize the patient information provided (age, medical history, symptoms).

========================
STEP 2 — Analyse ECG
========================
Follow EXACTLY this structure and numbering:

1. Rythme et fréquence
- Type de rythme (sinusal / non sinusal)
- Régularité (régulier / irrégulier)
- Fréquence cardiaque estimée (si possible)

2. Axe électrique
- Axe frontal (normal / dévié gauche / dévié droit)

3. Onde P et conduction auriculo-ventriculaire
- Onde P (présente / absente / anormale)
- Intervalle PR en ms 
- Bloc AV : absent / BAV I / BAV II / BAV complet

4. Complexe QRS
- Durée du QRS en ms
- Morphologie :
  - BBD
  - BBG
  - Hémibloc antérieur gauche (HBAG)
  - Hémibloc postérieur gauche (HBPG)
  - Bloc trifasciculaire (si critères réunis)

5. Repolarisation
- Segment ST (sus-décalage / sous-décalage / normal)
- Onde T (amplitude, symétrie, inversion)

6. Intervalle QT
- QT mesuré (si possible) en ms
- QTc estimé (normal / prolongé / raccourci)

7. Indices de Sokolow-Lyon
- en mm : si + ==> HVG ou HVD

========================
STEP 3 — Conclusion
========================
Provide a concise ECG conclusion integrating:
- ECG findings
- Patient age
- Symptoms and clinical context

========================
STEP 4 — Conduite à tenir
========================
Give SHORT and PRAGMATIC clinical advice adapted to the ECG and symptoms.


Keep this section brief and clinically realistic.

========================
IMPORTANT DISCLAIMER
========================
End with a medical disclaimer stating that this interpretation is for healthcare professional use and does not replace clinical judgment.

Patient data:
Age: {age or "Not provided"}
Antécédents médicaux: {history or "Not provided"}
Symptomatologie et examen clinique: {symptoms or "Not provided"}

Please proceed with the ECG analysis following the structure above.
"""


def generate_ecg_interpretation(
    image_path: str,
    age: Optional[str] = None,
    history: Optional[str] = None,
    symptoms: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate ECG interpretation using OpenRouter API with vision model
    Tries multiple models if one fails
    
    Args:
        image_path: Path to ECG image
        age: Patient age
        history: Medical history
        symptoms: Current symptoms
        
    Returns:
        Dict containing interpretation or error information
    """
    
    try:
        # Read and encode image as base64
        logger.info(f"Reading ECG image from: {image_path}")
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
        logger.info("Successfully loaded ECG image")
        
        # Build the prompt
        prompt = build_ecg_prompt(age, history, symptoms)
        
        # Try each model in order
        last_error = None
        for model in MODELS_TO_TRY:
            try:
                logger.info(f"Trying model: {model}")
                
                # Make API call with vision using OpenAI client
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1200  # Reduced to fit within your credit limit
                )
                
                interpretation_text = response.choices[0].message.content
                
                # Check if model refused (common refusal phrases)
                refusal_phrases = [
                    "i can't assist",
                    "i cannot assist",
                    "i'm sorry",
                    "i cannot provide",
                    "i can't provide",
                    "unable to assist"
                ]
                
                if any(phrase in interpretation_text.lower() for phrase in refusal_phrases):
                    logger.warning(f"Model {model} refused to analyze. Trying next model...")
                    last_error = f"Model {model} declined to analyze medical images"
                    continue
                
                logger.info(f"✅ Successfully received ECG interpretation from {model}")
                
                return {
                    "success": True,
                    "error": False,
                    "interpretation": interpretation_text,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
                
            except Exception as model_error:
                logger.warning(f"Model {model} failed: {str(model_error)}")
                last_error = str(model_error)
                continue
        
        # All models failed
        raise Exception(f"All models failed. Last error: {last_error}")
        
    except FileNotFoundError as e:
        logger.error(f"❌ ECG image file not found: {image_path}")
        return {
            "error": True,
            "message": f"ECG image file not found: {image_path}",
            "fallback_info": {
                "patient_age": age,
                "medical_history": history,
                "symptoms": symptoms,
                "recommendation": "Please ensure the ECG image was uploaded correctly and try again."
            }
        }
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"❌ Error generating ECG interpretation: {error_message}")
        
        # Check for specific error types
        if "402" in error_message or "payment" in error_message.lower():
            user_message = "Insufficient credits in OpenRouter account. Please add credits to continue."
        elif "401" in error_message or "authentication" in error_message.lower():
            user_message = "API authentication failed. Please check your API key."
        elif "429" in error_message or "rate limit" in error_message.lower():
            user_message = "Rate limit exceeded. Please try again in a few moments."
        elif "timeout" in error_message.lower():
            user_message = "Request timeout. The AI service took too long to respond."
        elif "connection" in error_message.lower():
            user_message = "Unable to connect to the AI service. Please check your internet connection."
        else:
            user_message = f"Unable to analyze ECG: {error_message}"
        
        return {
            "error": True,
            "message": user_message,
            "fallback_info": {
                "patient_age": age,
                "medical_history": history,
                "symptoms": symptoms,
                "recommendation": "Please consult with a healthcare professional for proper ECG interpretation."
            }
        }

