import os
import config

from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph

# Modern color scheme
COLORS = {
    "primary": colors.HexColor("#1a237e"),  # Deep blue
    "secondary": colors.HexColor("#546e7a"),  # Blue gray
    "accent": colors.HexColor("#ff6f00"),  # Amber
    "light": colors.HexColor("#f5f5f5"),  # Light gray
    "dark": colors.HexColor("#212121"),  # Almost black
}


def generate_doc_template(name, job_data_location):
    """
    Generate and return a SimpleDocTemplate for a modern resum'w e PDF.

    Args:
        name (str): The name of the resume author.
        job_data_location (str): The path where the PDF will be saved.

    Returns:
        tuple: A tuple containing the document template for the resume PDF and the PDF location.
    """
    author_name_formatted = name.replace(" ", "_") + "_modern_resume"
    pdf_location = os.path.join(job_data_location, f"{author_name_formatted}.pdf")
    doc = SimpleDocTemplate(
        pdf_location,
        pagesize=A4,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        title=f"{author_name_formatted}",
        author=name,
    )
    return (doc, pdf_location)


DEFAULT_PADDING = (2, 2)
DOCUMENT_ALIGNMENT = [
    ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]
DEBUG_STYLE = ("GRID", (0, 0), (-1, -1), 0, colors.black)

PAGE_WIDTH, PAGE_HEIGHT = A4
FULL_COLUMN_WIDTH = PAGE_WIDTH - 1 * inch

# Font definitions - using standard ReportLab fonts for better compatibility
FONT_PATHS = {
    "regular": os.path.join(config.RESOURCES_PATH, "fonts/calibri.ttf"),
    "bold": os.path.join(config.RESOURCES_PATH, "fonts/calibrib.ttf"),
    "italic": os.path.join(config.RESOURCES_PATH, "fonts/calibrii.ttf"),
}
FONT_NAMES = {
    "regular": "FONT_Modern_Regular",
    "bold": "FONT_Modern_Bold",
    "italic": "FONT_Modern_Italic",
}

sample_style_sheets = getSampleStyleSheet()

# Modern styles with color accent and more whitespace
PARAGRAPH_STYLES = {
    "bullet_points": ParagraphStyle(
        name="modern_bullet_points",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=0,
        justifyBreaks=0,
        justifyLastLine=0,
        firstLineIndent=-10,
        bulletIndent=5,
    ),
    "last_bullet_point": ParagraphStyle(
        name="modern_last_bullet_point",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=0,
        justifyBreaks=0,
        justifyLastLine=0,
        firstLineIndent=-10,
        bulletIndent=5,
        spaceAfter=5,
    ),
    "name": ParagraphStyle(
        name="modern_name",
        fontName=FONT_NAMES["bold"],
        fontSize=18,
        textColor=COLORS["primary"],
        alignment=TA_CENTER,
        leading=22,
        spaceAfter=5,
    ),
    "link": ParagraphStyle(
        name="modern_link",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        textColor=COLORS["accent"],
        underline=True,
    ),
    "link-no-hyperlink": ParagraphStyle(
        name="modern_link_no_hyperlink",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        textColor=COLORS["secondary"],
    ),
    "normal": ParagraphStyle(
        name="modern_normal",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["dark"],
    ),
    "education": ParagraphStyle(
        name="modern_education",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["dark"],
    ),
    "space": ParagraphStyle(
        name="modern_space",
        fontName=FONT_NAMES["regular"],
        fontSize=0,
        leading=0,
    ),
    "skills": ParagraphStyle(
        name="modern_skills",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["dark"],
    ),
    "contact": ParagraphStyle(
        name="modern_contact",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=COLORS["secondary"],
        spaceAfter=15,
    ),
    "section": ParagraphStyle(
        name="modern_section",
        fontName=FONT_NAMES["bold"],
        fontSize=12,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=16,
        spaceBefore=10,
        spaceAfter=5,
    ),
    "objective": ParagraphStyle(
        name="modern_objective",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=COLORS["dark"],
        spaceAfter=10,
    ),
    "company_heading": ParagraphStyle(
        name="modern_company_heading",
        fontName=FONT_NAMES["bold"],
        fontSize=11,
        leading=14,
        textColor=COLORS["dark"],
    ),
    "company_title": ParagraphStyle(
        name="modern_company_title",
        fontName=FONT_NAMES["italic"],
        fontSize=10,
        leading=14,
        textColor=COLORS["secondary"],
    ),
    "company_duration": ParagraphStyle(
        name="modern_company_duration",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "company_location": ParagraphStyle(
        name="modern_company_location",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
}
