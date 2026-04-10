from __future__ import annotations

from html import escape
from pathlib import Path

from logic.models import Project


def _image_html(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    uri = p.resolve().as_uri()
    return f'<img src="{uri}" style="width:100%;max-height:260px;object-fit:cover;margin:8px 0;border-radius:6px;" />'


def render_html(project: Project) -> str:
    logo_uri = ""
    logo_path = Path(project.logo_path)
    if logo_path.exists():
        logo_uri = logo_path.resolve().as_uri()

    article_blocks = []
    for index, article in enumerate(project.articles, start=1):
        images = "".join(_image_html(i) for i in article.images)
        banner = (
            f'<div class="breaking">عاجل | Breaking News</div>'
            if article.is_breaking
            else ""
        )
        article_blocks.append(
            f"""
            <section class=\"article\">
                {banner}
                <h2>{escape(article.title or f'عنوان المقال {index}')}</h2>
                <div class=\"meta\">{escape(article.author or 'غير محدد')} | {escape(article.date_text)} | {escape(article.location or 'غير محدد')} | {escape(article.category)}</div>
                <div class=\"columns\">{escape(article.content).replace(chr(10), '<br/>')}</div>
                {images}
            </section>
            """
        )

    return f"""
    <html dir=\"rtl\" lang=\"ar\">
    <head>
      <meta charset=\"UTF-8\" />
      <style>
        @page {{ size: A4; margin: 18mm 15mm; }}
        body {{ font-family: 'Segoe UI', 'Noto Naskh Arabic', sans-serif; color: #1a1a1a; }}
        .header {{ border-bottom: 4px solid {project.primary_color}; padding-bottom: 10px; margin-bottom: 12px; display:flex; align-items:center; gap:14px; }}
        .header img {{ width: 82px; height: 82px; border-radius: 50%; border: 2px solid {project.secondary_color}; }}
        .name {{ font-size: 32px; font-weight: 800; color: {project.secondary_color}; }}
        .issue {{ color: {project.primary_color}; font-weight: 600; }}
        .article {{ margin: 14px 0 24px; border-bottom: 1px dashed #888; padding-bottom: 12px; }}
        .article h2 {{ margin: 0 0 8px; color: {project.primary_color}; font-size: 24px; }}
        .meta {{ font-size: 12px; color: #555; margin-bottom: 8px; }}
        .columns {{ column-count: 2; column-gap: 22px; text-align: justify; line-height: 1.9; font-size: 14px; }}
        .breaking {{ display:inline-block; background:#d50000; color:#fff; padding:4px 10px; border-radius:4px; font-weight:700; margin-bottom:8px; }}
        .footer {{ position: fixed; bottom: 4mm; left: 0; right: 0; text-align: center; color:#666; font-size:11px; }}
      </style>
    </head>
    <body>
      <header class=\"header\">
        {'<img src="'+logo_uri+'" />' if logo_uri else ''}
        <div>
            <div class=\"name\">{escape(project.newspaper_name)}</div>
            <div class=\"issue\">{escape(project.issue_title)} - قالب: {escape(project.template_name)}</div>
        </div>
      </header>
      {''.join(article_blocks) if article_blocks else '<p>لا توجد مقالات بعد.</p>'}
      <div class=\"footer\">صفحة <span class=\"pageNumber\"></span> | Young Journalists Club</div>
    </body>
    </html>
    """
