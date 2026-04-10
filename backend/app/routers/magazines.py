import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Article, Magazine, MagazineCreate, MagazineOut
from ..utils.pdf_generator import generate_pdf, generate_png


router = APIRouter(prefix="/magazines", tags=["magazines"])


@router.get("", response_model=list[MagazineOut])
def list_magazines(db: Session = Depends(get_db)):
    return db.query(Magazine).order_by(Magazine.created_at.desc()).all()


@router.post("", response_model=MagazineOut)
def create_magazine(payload: MagazineCreate, db: Session = Depends(get_db)):
    selected_articles = db.query(Article).filter(Article.id.in_(payload.article_ids)).all() if payload.article_ids else []

    layout = {
        "columns": 2,
        "article_count": len(selected_articles),
        "article_ids": payload.article_ids,
    }

    magazine = Magazine(
        name=payload.name,
        issue_number=payload.issue_number,
        primary_color=payload.primary_color,
        secondary_color=payload.secondary_color,
        logo_url=payload.logo_url,
        layout_json=json.dumps(layout, ensure_ascii=False),
    )
    db.add(magazine)
    db.commit()
    db.refresh(magazine)
    return magazine


@router.post("/{magazine_id}/export/pdf")
def export_magazine_pdf(magazine_id: int, db: Session = Depends(get_db)):
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")

    layout = json.loads(magazine.layout_json or "{}")
    article_ids = layout.get("article_ids", [])
    articles = db.query(Article).filter(Article.id.in_(article_ids)).all() if article_ids else db.query(Article).all()

    path = generate_pdf(
        name=magazine.name,
        issue_number=magazine.issue_number,
        articles=[{"title": a.title, "content": a.content} for a in articles],
        branding={"primary_color": magazine.primary_color, "secondary_color": magazine.secondary_color},
    )
    return {"file": str(path)}


@router.post("/{magazine_id}/export/png")
def export_magazine_png(magazine_id: int, db: Session = Depends(get_db)):
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")

    layout = json.loads(magazine.layout_json or "{}")
    article_ids = layout.get("article_ids", [])
    articles = db.query(Article).filter(Article.id.in_(article_ids)).all() if article_ids else db.query(Article).all()

    path = generate_png(
        name=magazine.name,
        issue_number=magazine.issue_number,
        articles=[{"title": a.title, "content": a.content} for a in articles],
        branding={"primary_color": magazine.primary_color, "secondary_color": magazine.secondary_color},
    )
    return {"file": str(path)}


@router.get("/download")
def download_file(path: str):
    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path)
