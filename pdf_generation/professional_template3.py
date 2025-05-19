import os
import config

from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

# Document alignment settings
DOCUMENT_ALIGNMENT = [
    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]

# Default padding settings
DEFAULT_PADDING = 3

# Professional ATS-focused color scheme - keep limited colors for ATS
COLORS = {
    "primary": colors.black,
    "secondary": colors.HexColor("#333333"),
    "light": colors.HexColor("#777777"),
    "section_bg": colors.HexColor("#F5F5F5"),
    "white": colors.white,
}


def generate_doc_template(name, job_data_location):
    """Generate and return a SimpleDocTemplate for a professional ATS-optimized resume PDF."""
    author_name_formatted = name.replace(" ", "_") + "_professional_ats_resume_2"
    pdf_location = os.path.join(job_data_location, f"{author_name_formatted}.pdf")

    # Create directory if it doesn't exist
    os.makedirs(job_data_location, exist_ok=True)

    # Check if file exists and handle permissions
    if os.path.exists(pdf_location):
        try:
            os.remove(pdf_location)
        except PermissionError:
            import time

            timestamp = int(time.time())
            pdf_location = os.path.join(
                job_data_location, f"{author_name_formatted}_{timestamp}.pdf"
            )

    doc = SimpleDocTemplate(
        pdf_location,
        pagesize=A4,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=f"{author_name_formatted}",
        author=name,
    )
    return (doc, pdf_location)


# Define fonts - Using Times for very high ATS readability
FONT_PATHS = {
    "regular": os.path.join(config.RESOURCES_PATH, "fonts/GEORGIA.ttf"),
    "bold": os.path.join(config.RESOURCES_PATH, "fonts/GEORGIAB.ttf"),
    "italic": os.path.join(config.RESOURCES_PATH, "fonts/GEORGIAI.ttf"),
}

FONT_NAMES = {
    "regular": "FONT_ATS_Regular",
    "bold": "FONT_ATS_Bold",
    "italic": "FONT_ATS_Italic",
}

# Template dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4
FULL_COLUMN_WIDTH = PAGE_WIDTH - 1.4 * inch

# Paragraph styles optimized for ATS readability
PARAGRAPH_STYLES = {
    "name": ParagraphStyle(
        name="ats_name",
        fontName=FONT_NAMES["bold"],
        fontSize=14,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=16,
        spaceAfter=0,
    ),
    "contact": ParagraphStyle(
        name="ats_contact",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=COLORS["secondary"],
        spaceAfter=12,
    ),
    "section": ParagraphStyle(
        name="ats_section",
        fontName=FONT_NAMES["bold"],
        fontSize=12,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=14,
        spaceBefore=12,
        spaceAfter=6,
        backColor=COLORS["section_bg"],
        borderPadding=5,
    ),
    "objective": ParagraphStyle(
        name="ats_objective",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=COLORS["primary"],
        spaceAfter=10,
    ),
    "company_heading": ParagraphStyle(
        name="ats_company_heading",
        fontName=FONT_NAMES["bold"],
        fontSize=11,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "company_title": ParagraphStyle(
        name="ats_company_title",
        fontName=FONT_NAMES["italic"],
        fontSize=10,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "company_duration": ParagraphStyle(
        name="ats_company_duration",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "company_location": ParagraphStyle(
        name="ats_company_location",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "bullet_points": ParagraphStyle(
        name="ats_bullet_points",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["primary"],
        firstLineIndent=-10,
    ),
    "last_bullet_point": ParagraphStyle(
        name="ats_last_bullet_point",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["primary"],
        firstLineIndent=-10,
        spaceAfter=6,
    ),
    "education": ParagraphStyle(
        name="ats_education",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "skills": ParagraphStyle(
        name="ats_skills",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "skill_category": ParagraphStyle(
        name="ats_skill_category",
        fontName=FONT_NAMES["bold"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
}


def build_professional_ats_resume(doc, data):
    """Build a professional ATS-optimized resume with clear labels and standard sections."""
    story = []

    # Header with name and contact info in clearly labeled format
    name_str = data["basic"]["name"]
    story.append(Paragraph(name_str, PARAGRAPH_STYLES["name"]))

    # Contact details with explicit labels for ATS parsing
    contact_lines = []
    contact_lines.append(
        f"Email: {data['basic']['email']} | Phone: {data['basic']['phone']}"
    )

    # Add address with label
    address_line = f"Address: {data['basic']['address']}"
    contact_lines.append(address_line)

    # Add websites with labels
    website_parts = []
    for website in data["basic"]["websites"]:
        website_clean = (
            website.replace("https://", "").replace("http://", "").replace("www.", "")
        )
        website_parts.append(f"Website: {website_clean}")

    if website_parts:
        contact_lines.append(" | ".join(website_parts))

    # Add contact info as individual paragraphs
    for line in contact_lines:
        story.append(Paragraph(line, PARAGRAPH_STYLES["contact"]))

    # Professional Summary - standard section name for ATS
    story.append(Paragraph("PROFESSIONAL SUMMARY", PARAGRAPH_STYLES["section"]))
    story.append(Paragraph(data["objective"], PARAGRAPH_STYLES["objective"]))

    # Work Experience - standard section name for ATS
    story.append(Paragraph("WORK EXPERIENCE", PARAGRAPH_STYLES["section"]))

    for job in data["experiences"]:
        # Job header with company and duration
        duration = f"{job['titles'][0]['startdate']} - {job['titles'][0]['enddate']}"

        if not job["skip_name"]:
            # Format: Company Name (clear for ATS)
            story.append(Paragraph(job["company"], PARAGRAPH_STYLES["company_heading"]))

            # Format: Job Title, Location | Duration (clear for ATS)
            job_details = f"{job['titles'][0]['name']}, {job['location']} | {duration}"
            story.append(Paragraph(job_details, PARAGRAPH_STYLES["company_title"]))
        else:
            # Format: Job Title | Duration (clear for ATS)
            job_details = f"{job['titles'][0]['name']} | {duration}"
            story.append(Paragraph(job_details, PARAGRAPH_STYLES["company_title"]))

        # Job highlights with standard bullet points
        for i, bullet_point in enumerate(job["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(job["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            story.append(Paragraph(f"• {bullet_point}", style))

    # Skills section - clear labeling for ATS
    story.append(Paragraph("SKILLS", PARAGRAPH_STYLES["section"]))

    # Skills in keyword-rich format
    for group in data["skills"]:
        group_keys = list(group.keys())
        skill_type = group[group_keys[0]]
        skills_list = group[group_keys[1]]

        # Format: Category: skill1, skill2, skill3
        skill_text = f"{skill_type}: {', '.join(skills_list)}"
        story.append(Paragraph(skill_text, PARAGRAPH_STYLES["skills"]))
        story.append(Spacer(1, 4))

    # Education section - standard format for ATS
    story.append(Paragraph("EDUCATION", PARAGRAPH_STYLES["section"]))

    for edu in data["education"]:
        school = edu["school"]
        degrees = ", ".join(edu["degrees"][0]["names"])

        # Format: School Name - Degree(s)
        education_text = f"{school} - {degrees}"
        story.append(Paragraph(education_text, PARAGRAPH_STYLES["education"]))
        story.append(Spacer(1, 4))

    # Projects section
    story.append(Paragraph("PROJECTS", PARAGRAPH_STYLES["section"]))

    for project in data["projects"]:
        project_name = project["name"]
        project_date = project["date"]

        # Project header with name and date
        project_header = f"{project_name} | {project_date}"
        story.append(Paragraph(project_header, PARAGRAPH_STYLES["company_heading"]))

        # Add link as separate line if present (better for ATS)
        if project["show_link"]:
            raw_link = project["link"]
            clean_link = (
                raw_link.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
            )
            link_text = f"Project Link: {clean_link}"
            story.append(Paragraph(link_text, PARAGRAPH_STYLES["company_title"]))

        # Project highlights
        for i, bullet_point in enumerate(project["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(project["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            story.append(Paragraph(f"• {bullet_point}", style))

    return story
