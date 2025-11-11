from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat


app = FastAPI(title='InsuranceAI Backend')
app.include_router(chat.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "InsuranceAI Backend is running"}