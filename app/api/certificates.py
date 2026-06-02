from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.crud.certificate import get_certificate_by_user_course
from app.models.certificate import Certificate
from app.core.certificate_generator import generate_certificate_pdf
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from io import BytesIO

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("/verify/{certificate_id}")
def verify_certificate(certificate_id: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.certificate_id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return JSONResponse({"certificate_id": cert.certificate_id, "user_id": cert.user_id, "course_id": cert.course_id, "issued_at": cert.issued_at.isoformat()})


@router.get("/download/{certificate_id}")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.certificate_id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    user_name = cert.user.full_name or cert.user.email
    course_title = cert.course.title
    issued_at = cert.issued_at.isoformat()
    pdf_bytes = generate_certificate_pdf(user_name, course_title, issued_at, cert.certificate_id)
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=certificate_{certificate_id}.pdf"})


@router.get("/my")
def my_certificates(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Return all certificates for the current user as JSON."""
    certs = db.query(Certificate).filter(Certificate.user_id == current_user.id).all()
    return [
        {
            "certificate_id": c.certificate_id,
            "course_id": c.course_id,
            "course_title": c.course.title if c.course else None,
            "issued_at": c.issued_at.isoformat(),
        }
        for c in certs
    ]
