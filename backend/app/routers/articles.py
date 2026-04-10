from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai.ai_manager import AIManager
from ..database import get_db
from ..models import Article, ArticleGenerateRequest, ArticleOut, ArticleUpdate


router = APIRouter(prefix="/articles", tags=["articles"])
ai_manager = AIManager()


@router.get("", response_model=list[ArticleOut])
def list_articles(db: Session = Depends(get_db)):
    return db.query(Article).order_by(Article.created_at.desc()).all()


@router.post("/generate", response_model=ArticleOut)
def generate_article(payload: ArticleGenerateRequest, db: Session = Depends(get_db)):
    content, _mode = ai_manager.generate_article(
        author_name=payload.author_name,
        title=payload.title,
        topic=payload.topic,
        category=payload.category,
        requested_mode=payload.mode,
    )

    article = Article(
        author_name=payload.author_name,
        title=payload.title,
        topic=payload.topic,
        category=payload.category,
        content=content,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(article_id: int, payload: ArticleUpdate, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(article, field, value)

    db.commit()
    db.refresh(article)
    return article


@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()
    return {"message": "Deleted"}
