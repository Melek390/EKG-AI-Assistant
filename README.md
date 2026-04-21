# ECG AI Analysis Platform

A web application for medical professionals to upload and analyze electrocardiograms using AI-powered interpretation. Built with FastAPI and PostgreSQL, it integrates multimodal vision models via OpenRouter to generate structured, clinically relevant ECG reports.

> Built by medical residents, focused on real clinical workflows.

---

## Features

- **User authentication** — Secure signup/login with Argon2 password hashing and session management
- **ECG upload** — Upload ECG images with patient context (age, symptoms, medical history)
- **AI-powered analysis** — Structured ECG interpretation using vision LLMs (Gemini, Claude, GPT-4o Mini)
- **ECG history** — View and delete previous analyses per user
- **Bilingual output** — AI reports support French and English
- **Responsive UI** — Clean, dark-themed Bootstrap 5 frontend

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.10+ |
| Database | PostgreSQL + SQLAlchemy ORM |
| Auth | Session middleware + Passlib (Argon2) |
| AI | OpenRouter API (Gemini Flash 1.5, Claude 3 Haiku, GPT-4o Mini) |
| Frontend | Jinja2 Templates, Bootstrap 5, WOW.js |

---

## Project Structure

```
ECG app (fast api-sql db)/
├── main.py                     # FastAPI app entry point
├── .env                        # Environment variables (not committed)
├── .env.example                # Environment variable template
├── command.txt                 # Useful startup commands
├── database/
│   ├── database.py             # SQLAlchemy engine & session
│   ├── security.py             # Password hashing
│   └── initdb.py               # Database table creation script
├── models/
│   ├── user.py                 # User ORM model
│   └── ecg.py                  # ECG record ORM model
├── routers/
│   ├── login.py                # Login & logout routes
│   ├── signup.py               # User registration routes
│   ├── ecg.py                  # ECG upload routes
│   ├── ecghistory.py           # ECG history routes
│   └── ecganalysisresult.py    # AI analysis result routes
├── dependencies/
│   └── auth.py                 # Login-required dependency
├── LMMintegration/
│   └── ecgassistant.py         # OpenRouter AI integration
├── templates/                  # Jinja2 HTML templates
└── assets/                     # Static files (CSS, JS, images, fonts)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL (running locally or remotely)
- An [OpenRouter](https://openrouter.ai) API key

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ecg-ai-platform.git
cd ecg-ai-platform
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is missing, install the core packages manually:
> ```bash
> pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[argon2] python-multipart python-dotenv jinja2 openai
> ```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL="postgresql+psycopg2://your_user:your_password@localhost:5432/ecg_app"
ECG_ASSISTANT_KEY="your-openrouter-api-key"
SECRET_KEY="your-random-secret-key"
```

### 5. Create the database

Create a PostgreSQL database named `ecg_app` (or whatever you set in `DATABASE_URL`), then run:

```bash
python database/initdb.py
```

### 6. Run the application

```bash
python -m uvicorn main:app --reload
```

The app will be available at [http://localhost:8000](http://localhost:8000).

---

## API Endpoints

| Method | Path | Auth Required | Description |
|--------|------|:---:|-------------|
| GET | `/` | No | Landing page |
| GET | `/signup` | No | Registration form |
| POST | `/signup` | No | Register new user |
| GET | `/login` | No | Login form |
| POST | `/login` | No | Authenticate user |
| GET | `/logout` | Yes | Log out and clear session |
| GET | `/ecg` | Yes | ECG upload form |
| POST | `/ecg` | Yes | Submit ECG image + patient data |
| GET | `/ecghistory` | Yes | List user's ECG history |
| DELETE | `/ecg/{ecg_id}` | Yes | Delete an ECG record |
| GET | `/ecg/{ecg_id}/result` | Yes | Generate AI analysis for an ECG |

---

## Database Schema

### `users`

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `email` | String (unique) | Login email |
| `hashed_password` | String | Argon2 hashed |
| `full_name` | String | Optional display name |
| `specialty` | String | Medical specialty |
| `institution` | String | Hospital / clinic |
| `role` | Enum | `doctor`, `resident`, or `admin` |
| `is_active` | Boolean | Account status |
| `created_at` | DateTime | Registration timestamp |

### `ecgdatabase`

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `user_id` | UUID (FK) | Reference to user (cascade delete) |
| `age` | Integer | Patient age |
| `history` | Text | Medical history & medications |
| `symptoms` | Text | Clinical symptoms & exam findings |
| `ecg_image_path` | String | Path to uploaded image |
| `created_at` | DateTime | Submission timestamp |

---

## AI Analysis

ECG interpretation is performed by calling the [OpenRouter](https://openrouter.ai) API with a vision-capable model. The system automatically tries models in the following order:

1. `google/gemini-flash-1.5`
2. `anthropic/claude-3-haiku`
3. `openai/gpt-4o-mini`

Each analysis produces a structured clinical report covering:

- Rhythm and rate
- Electrical axis
- P waves, PR interval, QRS complex
- ST segment and T waves
- QT/QTc interval
- Sokolow-Lyon index
- Clinical interpretation and recommendations

---

## Security Notes

Before deploying or sharing this project, make sure to:

- [ ] Keep `.env` out of version control (already in `.gitignore`)
- [ ] Replace the hardcoded session `SECRET_KEY` in `main.py` with `os.environ.get("SECRET_KEY")`
- [ ] Rotate your OpenRouter API key if it was ever committed to git
- [ ] Use a strong, random `SECRET_KEY` for production sessions
- [ ] Consider HTTPS and proper CORS settings for production

---

## License

This project is intended for educational and research purposes. It is not a certified medical device. AI-generated ECG interpretations should always be reviewed by a qualified healthcare professional.

---

*© 2025 Medical AI Platform — Designed by clinicians, powered by data.*
