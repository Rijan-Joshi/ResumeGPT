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

# Modern color scheme
COLORS = {
    "primary": colors.HexColor("#1A237E"),  # Deep blue
    "secondary": colors.HexColor("#546E7A"),  # Blue gray
    "accent": colors.HexColor("#FF6F00"),  # Amber
    "light": colors.HexColor("#F5F5F5"),  # Light gray
    "dark": colors.HexColor("#212121"),  # Almost black
    "white": colors.white,
}


def generate_doc_template(name, job_data_location):
    """
    Generate and return a SimpleDocTemplate for a modern resume PDF.
    """
    author_name_formatted = name.replace(" ", "_") + "_modern_resume"
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
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        title=f"{author_name_formatted}",
        author=name,
    )
    return (doc, pdf_location)


# Define styles for modern template
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

DEFAULT_PADDING = (2, 2)
DOCUMENT_ALIGNMENT = []  # We'll handle alignment differently for this template
DEBUG_STYLE = ("GRID", (0, 0), (-1, -1), 0, colors.black)

PAGE_WIDTH, PAGE_HEIGHT = A4
FULL_COLUMN_WIDTH = PAGE_WIDTH - 1.2 * inch

# Paragraph styles
PARAGRAPH_STYLES = {
    "name": ParagraphStyle(
        name="modern_name",
        fontName=FONT_NAMES["bold"],
        fontSize=20,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=24,
        spaceAfter=0,
    ),
    "title": ParagraphStyle(
        name="modern_title",
        fontName=FONT_NAMES["italic"],
        fontSize=12,
        textColor=COLORS["secondary"],
        alignment=TA_LEFT,
        leading=14,
        spaceAfter=6,
    ),
    "contact": ParagraphStyle(
        name="modern_contact",
        fontName=FONT_NAMES["regular"],
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=COLORS["secondary"],
        spaceAfter=10,
    ),
    "section": ParagraphStyle(
        name="modern_section",
        fontName=FONT_NAMES["bold"],
        fontSize=12,
        textColor=COLORS["white"],
        alignment=TA_LEFT,
        leading=14,
        spaceBefore=10,
        spaceAfter=6,
        leftIndent=10,
    ),
    "objective": ParagraphStyle(
        name="modern_objective",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=COLORS["dark"],
        spaceAfter=8,
    ),
    "company_heading": ParagraphStyle(
        name="modern_company_heading",
        fontName=FONT_NAMES["bold"],
        fontSize=11,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "company_title": ParagraphStyle(
        name="modern_company_title",
        fontName=FONT_NAMES["italic"],
        fontSize=10,
        leading=12,
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
    "bullet_points": ParagraphStyle(
        name="modern_bullet_points",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["dark"],
        firstLineIndent=-10,
    ),
    "last_bullet_point": ParagraphStyle(
        name="modern_last_bullet_point",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["dark"],
        firstLineIndent=-10,
        spaceAfter=6,
    ),
    "education": ParagraphStyle(
        name="modern_education",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["dark"],
    ),
    "skills": ParagraphStyle(
        name="modern_skills",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["dark"],
    ),
    "skill_category": ParagraphStyle(
        name="modern_skill_category",
        fontName=FONT_NAMES["bold"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
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
    "space": ParagraphStyle(
        name="modern_space",
        fontName=FONT_NAMES["regular"],
        fontSize=0,
        leading=0,
    ),
}


def build_modern_resume(doc, data):
    """
    Build a modern resume with attractive section headers and clean layout.
    """
    story = []

    # Header with name and contact info
    header_data = [
        [
            Paragraph(data["basic"]["name"], PARAGRAPH_STYLES["name"]),
        ]
    ]

    # If there's a current job title, add it under the name
    if data["experiences"] and not data["experiences"][0]["skip_name"]:
        current_title = data["experiences"][0]["titles"][0]["name"]
        header_data.append([Paragraph(current_title, PARAGRAPH_STYLES["title"])])

    # Create contact information
    contact_parts = []
    contact_parts.append(data["basic"]["email"])
    contact_parts.append(data["basic"]["phone"])

    # Add websites
    for website in data["basic"]["websites"]:
        website_clean = (
            website.replace("https://", "").replace("http://", "").replace("www.", "")
        )
        contact_parts.append(website_clean)

    # Add address
    contact_parts.append(data["basic"]["address"])

    # Join with separator
    contact_text = " | ".join(contact_parts)
    header_data.append([Paragraph(contact_text, PARAGRAPH_STYLES["contact"])])

    # Create the header table
    header = Table(
        header_data,
        colWidths=[FULL_COLUMN_WIDTH],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        ),
    )
    story.append(header)

    # Create modern section header with background color
    def create_section_header(title):
        header_table = Table(
            [[Paragraph(title.upper(), PARAGRAPH_STYLES["section"])]],
            colWidths=[FULL_COLUMN_WIDTH],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), COLORS["primary"]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            ),
        )
        return header_table

    # Objective section
    story.append(create_section_header("PROFESSIONAL SUMMARY"))
    story.append(Paragraph(data["objective"], PARAGRAPH_STYLES["objective"]))

    # Experience section
    story.append(create_section_header("EXPERIENCE"))

    for job in data["experiences"]:
        # Job header with company and duration
        duration = f"{job['titles'][0]['startdate']}-{job['titles'][0]['enddate']}"

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

        # Job highlights (bullet points)
        for i, bullet_point in enumerate(job["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(job["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            story.append(Paragraph(f"• {bullet_point}", style))

        story.append(Spacer(1, 8))

    # Projects section
    story.append(create_section_header("PROJECTS"))

    for project in data["projects"]:
        project_name = project["name"]

        if project["show_link"]:
            raw_link = project["link"]
            clean_link = (
                raw_link.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
            )

            if project["hyperlink"]:
                # No color attribute to avoid issues
                link_text = f"<a href='{raw_link}'>{clean_link}</a>"
            else:
                link_text = clean_link

            project_header = f"<b>{project_name}</b>: {link_text}"
        else:
            project_header = f"<b>{project_name}</b>"

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

        # Project highlights (bullet points)
        for i, bullet_point in enumerate(project["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(project["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            story.append(Paragraph(f"• {bullet_point}", style))

        story.append(Spacer(1, 8))

    # Skills section
    story.append(create_section_header("SKILLS"))

    skills_data = []
    skills_row = []
    col_count = 0

    for group in data["skills"]:
        group_keys = list(group.keys())
        skill_type = group[group_keys[0]]
        skills_list = group[group_keys[1]]

        skill_text = f"<b>{skill_type}</b>: {', '.join(skills_list)}"

        skills_row.append(Paragraph(skill_text, PARAGRAPH_STYLES["skills"]))
        col_count += 1

        # Two columns per row
        if col_count == 2:
            skills_data.append(skills_row)
            skills_row = []
            col_count = 0

    # Add any remaining skills
    if skills_row:
        if len(skills_row) == 1:
            skills_row.append(Paragraph("", PARAGRAPH_STYLES["space"]))
        skills_data.append(skills_row)

    # Create skills table
    if skills_data:
        skills_table = Table(
            skills_data,
            colWidths=[FULL_COLUMN_WIDTH * 0.48, FULL_COLUMN_WIDTH * 0.48],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ]
            ),
        )
        story.append(skills_table)

    # Education section
    story.append(create_section_header("EDUCATION"))

    for edu in data["education"]:
        school = edu["school"]
        degrees = ", ".join(edu["degrees"][0]["names"])

        education_text = f"<b>{school}</b>, {degrees}"
        story.append(Paragraph(education_text, PARAGRAPH_STYLES["education"]))
        story.append(Spacer(1, 4))

    return story
