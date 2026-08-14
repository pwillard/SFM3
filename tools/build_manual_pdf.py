from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "SFM3_Manual.md"
OUTPUT = ROOT / "docs" / "SFM3_Manual.pdf"


def inline_markup(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(0.75 * inch, 0.45 * inch, "Open Rails Shape File Manager 3.0 User Manual")
    canvas.drawRightString(7.75 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_story(markdown_text: str):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ManualTitle", parent=styles["Title"], fontSize=22, leading=27, spaceAfter=18))
    styles.add(ParagraphStyle(name="ManualSubtitle", parent=styles["Normal"], fontSize=12, leading=16, textColor=colors.darkslategray, spaceAfter=20))
    styles.add(ParagraphStyle(name="Heading2Manual", parent=styles["Heading2"], fontSize=14, leading=18, spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="BodyManual", parent=styles["BodyText"], fontSize=10.25, leading=14, spaceAfter=7))
    styles.add(ParagraphStyle(name="BulletManual", parent=styles["BodyText"], fontSize=10.25, leading=14, leftIndent=12))
    styles.add(ParagraphStyle(name="CodeManual", parent=styles["Code"], fontName="Courier", fontSize=8.5, leading=11, backColor=colors.whitesmoke, borderColor=colors.lightgrey, borderWidth=0.4, borderPadding=5, spaceBefore=4, spaceAfter=8))

    story = []
    lines = markdown_text.splitlines()
    paragraph: list[str] = []
    bullets: list[str] = []
    code: list[str] = []
    in_code = False
    first_heading = True

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), styles["BodyManual"]))
            paragraph = []

    def flush_bullets() -> None:
        nonlocal bullets
        if bullets:
            items = [ListItem(Paragraph(inline_markup(item), styles["BodyManual"]), leftIndent=12) for item in bullets]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=18, bulletFontName="Helvetica", bulletFontSize=7))
            story.append(Spacer(1, 4))
            bullets = []

    def flush_code() -> None:
        nonlocal code
        if code:
            story.append(Preformatted("\n".join(code), styles["CodeManual"]))
            code = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                in_code = False
                flush_code()
            else:
                flush_paragraph()
                flush_bullets()
                in_code = True
                code = []
            continue
        if in_code:
            code.append(line)
            continue
        if not line:
            flush_paragraph()
            flush_bullets()
            continue
        if line.startswith("# "):
            flush_paragraph()
            flush_bullets()
            if not first_heading:
                story.append(PageBreak())
            story.append(Paragraph(inline_markup(line[2:]), styles["ManualTitle"]))
            first_heading = False
            continue
        if line.startswith("## "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(inline_markup(line[3:]), styles["Heading2Manual"]))
            continue
        if line.startswith("### "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(inline_markup(line[4:]), styles["Heading3"]))
            continue
        if line.startswith("- "):
            flush_paragraph()
            bullets.append(line[2:])
            continue
        paragraph.append(line)

    flush_paragraph()
    flush_bullets()
    flush_code()
    return story


def main() -> int:
    markdown_text = SOURCE.read_text(encoding="utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="SFM3_Manual-build-", suffix=".pdf", dir=OUTPUT.parent)
    os.close(fd)
    Path(temp_name).unlink(missing_ok=True)
    doc = SimpleDocTemplate(
        temp_name,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Open Rails Shape File Manager 3.0 User Manual",
        author="SFM3 Project",
    )
    doc.build(build_story(markdown_text), onFirstPage=footer, onLaterPages=footer)
    try:
        Path(temp_name).replace(OUTPUT)
    except OSError as exc:
        print(f"Built {temp_name}")
        print(f"Unable to replace {OUTPUT}: {exc}")
        print("Close any PDF viewer using the manual, then copy the built file over the final PDF.")
        return 1
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
