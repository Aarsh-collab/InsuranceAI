from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.lifeInsurance import life_prediction
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from core.rate_limiter import limiter
from routers import dec_page, context_router, session_router
from routers.admin import leads_router, messages_router, sessions_router, user_router
from db.database import init_db
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(title='InsuranceAI Backend')

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
app.add_middleware(SlowAPIMiddleware)

@app.get("/health")
def health_check():
    return{"status": "healthy"}

app.include_router(context_router.router)
app.include_router(session_router.router)
app.include_router(life_prediction.router)
app.include_router(dec_page.router)
app.include_router(leads_router.router)
app.include_router(user_router.router)
app.include_router(sessions_router.router)
app.include_router(messages_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {"message": "InsuranceAI Backend is running"}
