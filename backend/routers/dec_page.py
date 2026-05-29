from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from db.database import get_db
from db import models
from services.dec_page_parser import decPageParser
from sqlalchemy.orm import Session
import io
import pymupdf
from core.rate_limiter import limiter

router = APIRouter(prefix="/dec-page", tags=["Dec Page"])


@router.post("/upload")
@limiter.limit("5/minute")
async def decpage_endpoint(request: Request, session_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.session_id == session_id).first()
    
    #check if session exists
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    

    dec_page_table = db.query(models.DecPage).filter(models.DecPage.session_id == session_id).first()
    if not dec_page_table:
        dec_page_table = models.DecPage(
            session_id = session_id,
            insurance_type = session.insurance_type
            )
        db.add(dec_page_table)
        db.commit()
        db.refresh(dec_page_table)
    

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF is too large")

    pdf_stream = io.BytesIO(content)

    try:
        doc = pymupdf.open(stream=pdf_stream, filetype="pdf")
    except Exception:
        raise HTTPException(status_code=400, detail="invalid PDF file")
    
    dec_text = ""

    for page in doc:
        dec_text += page.get_text()

    reply = decPageParser(dec_text)
    doc.close()

    dec_page_table.parsed_json = reply
    dec_page_table.raw_text = dec_text

    db.commit()
    db.refresh(dec_page_table)
    return {"reply": reply}
