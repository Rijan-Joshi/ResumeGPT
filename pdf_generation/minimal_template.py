import os
import config

from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# Minimal ATS color scheme - optimized for parsing
COLORS = {
    "primary": colors.black,
    "secondary": colors.HexColor("#333333"),  # Dark gray
    "light": colors.HexColor("#777777"),  # Medium gray
    "white": colors.white,
}


def generate_doc_template(name, job_data_location):
    """Generate and return a SimpleDocTemplate for an ATS-focused minimal resume PDF."""
    author_name_formatted = name.replace(" ", "_") + "_minimal_ats_resume"
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


# Define fonts - standard fonts for ATS compatibility
FONT_PATHS = {
    "regular": os.path.join(config.RESOURCES_PATH, "fonts/calibri.ttf"),
    "bold": os.path.join(config.RESOURCES_PATH, "fonts/calibrib.ttf"),
    "italic": os.path.join(config.RESOURCES_PATH, "fonts/calibrii.ttf"),
}

FONT_NAMES = {
    "regular": "FONT_Minimal_Regular",
    "bold": "FONT_Minimal_Bold",
    "italic": "FONT_Minimal_Italic",
}

# Template dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4
FULL_COLUMN_WIDTH = PAGE_WIDTH - 1.4 * inch

# Paragraph styles - using standard fonts and formatting for ATS
PARAGRAPH_STYLES = {
    "name": ParagraphStyle(
        name="minimal_name",
        fontName=FONT_NAMES["bold"],
        fontSize=14,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=16,
        spaceAfter=0,
    ),
    "contact": ParagraphStyle(
        name="minimal_contact",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=COLORS["secondary"],
        spaceAfter=12,
    ),
    "section": ParagraphStyle(
        name="minimal_section",
        fontName=FONT_NAMES["bold"],
        fontSize=12,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=14,
        spaceBefore=12,
        spaceAfter=6,
        borderPadding=0,
    ),
    "objective": ParagraphStyle(
        name="minimal_objective",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=COLORS["primary"],
        spaceAfter=10,
    ),
    "company_heading": ParagraphStyle(
        name="minimal_company_heading",
        fontName=FONT_NAMES["bold"],
        fontSize=11,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "company_title": ParagraphStyle(
        name="minimal_company_title",
        fontName=FONT_NAMES["italic"],
        fontSize=10,
        leading=12,
        textColor=COLORS["light"],
    ),
    "company_duration": ParagraphStyle(
        name="minimal_company_duration",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["light"],
    ),
    "company_location": ParagraphStyle(
        name="minimal_company_location",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["light"],
    ),
    "bullet_points": ParagraphStyle(
        name="minimal_bullet_points",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["primary"],
        firstLineIndent=-10,
    ),
    "last_bullet_point": ParagraphStyle(
        name="minimal_last_bullet_point",
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
        name="minimal_education",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "skills": ParagraphStyle(
        name="minimal_skills",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "skill_category": ParagraphStyle(
        name="minimal_skill_category",
        fontName=FONT_NAMES["bold"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
}


def build_minimal_ats_resume(doc, data):
    """Build a minimal ATS-optimized resume with clean, simple layout."""
    story = []

    # Header with name and contact info - simple layout for ATS parsing
    name_str = data["basic"]["name"]
    story.append(Paragraph(name_str, PARAGRAPH_STYLES["name"]))

    # Contact details in clear, readable format for ATS
    email = f"Email: {data['basic']['email']}"
    phone = f"Phone: {data['basic']['phone']}"
    address = f"Address: {data['basic']['address']}"

    # Contact information as separate lines for better ATS parsing
    contact_info = [email, phone, address]

    # Add websites
    for i, website in enumerate(data["basic"]["websites"]):
        website_clean = (
            website.replace("https://", "").replace("http://", "").replace("www.", "")
        )
        contact_info.append(f"Website: {website_clean}")

    # Join with line breaks
    contact_text = " | ".join(contact_info)
    story.append(Paragraph(contact_text, PARAGRAPH_STYLES["contact"]))

    # Objective section - standard name for ATS
    story.append(Paragraph("PROFESSIONAL SUMMARY", PARAGRAPH_STYLES["section"]))
    story.append(Paragraph(data["objective"], PARAGRAPH_STYLES["objective"]))

    # Experience section - standard name for ATS
    story.append(Paragraph("WORK EXPERIENCE", PARAGRAPH_STYLES["section"]))

    for job in data["experiences"]:
        # Job header with company and duration
        duration = f"{job['titles'][0]['startdate']} - {job['titles'][0]['enddate']}"

        if not job["skip_name"]:
            job_table_data = [
                [
                    Paragraph(job["company"], PARAGRAPH_STYLES["company_heading"]),
                    Paragraph(duration, PARAGRAPH_STYLES["company_duration"]),
                ]
            ]

            job_table = Table(
                job_table_data,
                colWidths=[FULL_COLUMN_WIDTH * 0.7, FULL_COLUMN_WIDTH * 0.3],
                style=TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                ),
            )
            story.append(job_table)

            # Job title and location
            title_table_data = [
                [
                    Paragraph(
                        job["titles"][0]["name"], PARAGRAPH_STYLES["company_title"]
                    ),
                    Paragraph(job["location"], PARAGRAPH_STYLES["company_location"]),
                ]
            ]

            title_table = Table(
                title_table_data,
                colWidths=[FULL_COLUMN_WIDTH * 0.7, FULL_COLUMN_WIDTH * 0.3],
                style=TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                ),
            )
            story.append(title_table)
        else:
            # Just show title and duration
            job_table_data = [
                [
                    Paragraph(
                        job["titles"][0]["name"], PARAGRAPH_STYLES["company_title"]
                    ),
                    Paragraph(duration, PARAGRAPH_STYLES["company_duration"]),
                ]
            ]

            job_table = Table(
                job_table_data,
                colWidths=[FULL_COLUMN_WIDTH * 0.7, FULL_COLUMN_WIDTH * 0.3],
                style=TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                ),
            )
            story.append(job_table)

        # Job highlights with standard bullet points for ATS
        for i, bullet_point in enumerate(job["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(job["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            story.append(Paragraph(f"• {bullet_point}", style))

    # Projects section
    story.append(Paragraph("PROJECTS", PARAGRAPH_STYLES["section"]))

    for project in data["projects"]:
        project_name = project["name"]

        if project["show_link"]:
            raw_link = project["link"]
            clean_link = (
                raw_link.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
            )

            project_header = f"{project_name}: {clean_link}"
        else:
            project_header = f"{project_name}"

        # Project header with name/link and date
        project_table_data = [
            [
                Paragraph(project_header, PARAGRAPH_STYLES["company_heading"]),
                Paragraph(project["date"], PARAGRAPH_STYLES["company_duration"]),
            ]
        ]

        project_table = Table(
            project_table_data,
            colWidths=[FULL_COLUMN_WIDTH * 0.7, FULL_COLUMN_WIDTH * 0.3],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            ),
        )
        story.append(project_table)

        # Project highlights
        for i, bullet_point in enumerate(project["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(project["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            story.append(Paragraph(f"• {bullet_point}", style))

    # Skills section
    story.append(Paragraph("SKILLS", PARAGRAPH_STYLES["section"]))

    for group in data["skills"]:
        group_keys = list(group.keys())
        skill_type = group[group_keys[0]]
        skills_list = group[group_keys[1]]

        skill_text = f"{skill_type}: {', '.join(skills_list)}"
        story.append(Paragraph(skill_text, PARAGRAPH_STYLES["skills"]))
        story.append(Spacer(1, 4))

    # Education section
    story.append(Paragraph("EDUCATION", PARAGRAPH_STYLES["section"]))

    for edu in data["education"]:
        school = edu["school"]
        degrees = ", ".join(edu["degrees"][0]["names"])

        education_text = f"{school}, {degrees}"
        story.append(Paragraph(education_text, PARAGRAPH_STYLES["education"]))
        story.append(Spacer(1, 4))

    return story
