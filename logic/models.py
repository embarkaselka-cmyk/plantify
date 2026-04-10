from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import date
from typing import Any


@dataclass
class Article:
    title: str = ""
    author: str = ""
    category: str = "ثقافة"
    content: str = ""
    location: str = ""
    date_text: str = field(default_factory=lambda: date.today().isoformat())
    images: list[str] = field(default_factory=list)
    is_breaking: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Article":
        return cls(
            title=payload.get("title", ""),
            author=payload.get("author", ""),
            category=payload.get("category", "ثقافة"),
            content=payload.get("content", ""),
            location=payload.get("location", ""),
            date_text=payload.get("date_text", date.today().isoformat()),
            images=list(payload.get("images", [])),
            is_breaking=bool(payload.get("is_breaking", False)),
        )


@dataclass
class Project:
    newspaper_name: str = "نادي الصحفي الصغير"
    issue_title: str = "العدد الأسبوعي"
    primary_color: str = "#C62828"
    secondary_color: str = "#111111"
    logo_path: str = "assets/club_logo_placeholder.svg"
    template_name: str = "classic"
    articles: list[Article] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "newspaper_name": self.newspaper_name,
            "issue_title": self.issue_title,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "logo_path": self.logo_path,
            "template_name": self.template_name,
            "articles": [article.to_dict() for article in self.articles],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Project":
        return cls(
            newspaper_name=payload.get("newspaper_name", "نادي الصحفي الصغير"),
            issue_title=payload.get("issue_title", "العدد الأسبوعي"),
            primary_color=payload.get("primary_color", "#C62828"),
            secondary_color=payload.get("secondary_color", "#111111"),
            logo_path=payload.get("logo_path", "assets/club_logo_placeholder.svg"),
            template_name=payload.get("template_name", "classic"),
            articles=[Article.from_dict(i) for i in payload.get("articles", [])],
        )
