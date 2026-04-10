from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)


def _arabic_drawable(text: str) -> str:
    # Fallback: keep as-is. In production use arabic_reshaper + bidi for perfect shaping.
    return text


def generate_pdf(name: str, issue_number: str, articles: list[dict], branding: dict) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    output = EXPORT_DIR / f"{name}_{issue_number}_{timestamp}.pdf"

    c = canvas.Canvas(str(output), pagesize=A4)
    width, height = A4

    c.setFillColor(branding.get("primary_color", "#2563eb"))
    c.rect(0, height - 90, width, 90, fill=1, stroke=0)

    c.setFillColor("white")
    c.setFont("Helvetica-Bold", 22)
    c.drawRightString(width - 30, height - 55, _arabic_drawable(name))
    c.setFont("Helvetica", 12)
    c.drawRightString(width - 30, height - 75, _arabic_drawable(f"العدد: {issue_number}"))

    y = height - 120
    for idx, article in enumerate(articles, start=1):
        if y < 160:
            c.showPage()
            y = height - 60
        c.setFillColor(branding.get("secondary_color", "#0f172a"))
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(width - 30, y, _arabic_drawable(f"{idx}. {article['title']}"))
        y -= 18
        c.setFillColor("black")
        c.setFont("Helvetica", 11)
        for line in article["content"].split("\n")[:8]:
            c.drawRightString(width - 30, y, _arabic_drawable(line[:110]))
            y -= 14
        y -= 8

    c.save()
    return output


def generate_png(name: str, issue_number: str, articles: list[dict], branding: dict) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    output = EXPORT_DIR / f"{name}_{issue_number}_{timestamp}.png"

    image = Image.new("RGB", (1240, 1754), "white")
    draw = ImageDraw.Draw(image)

    try:
        font_title = ImageFont.truetype("DejaVuSans.ttf", 46)
        font_body = ImageFont.truetype("DejaVuSans.ttf", 26)
    except OSError:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    primary = branding.get("primary_color", "#2563eb")
    secondary = branding.get("secondary_color", "#0f172a")

    draw.rectangle((0, 0, 1240, 130), fill=primary)
    draw.text((50, 32), f"{name} - العدد {issue_number}", fill="white", font=font_title)

    y = 170
    for idx, article in enumerate(articles[:6], start=1):
        draw.text((70, y), f"{idx}) {article['title']}", fill=secondary, font=font_body)
        y += 38
        summary = article["content"].replace("\n", " ")[:180]
        draw.text((80, y), summary, fill="black", font=font_body)
        y += 84

    image.save(output)
    return output
