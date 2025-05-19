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

# Elegant color scheme
COLORS = {
    "primary": colors.HexColor("#3B0D11"),  # Rich burgundy
    "secondary": colors.HexColor("#565656"),  # Medium gray
    "accent": colors.HexColor("#8D1C24"),  # Deep red
    "light": colors.HexColor("#F1F1F1"),  # Off-white
    "white": colors.white,
    "black": colors.black,
}


def generate_doc_template(name, job_data_location):
    """Generate and return a SimpleDocTemplate for an elegant graduate resume PDF."""
    author_name_formatted = name.replace(" ", "_") + "_elegant_graduate_resume"
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
        leftMargin=0.8 * inch,
        rightMargin=0.8 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
        title=f"{author_name_formatted}",
        author=name,
    )
    return (doc, pdf_location)


# Define fonts - using Georgia for elegant look
FONT_PATHS = {
    "regular": os.path.join(config.RESOURCES_PATH, "fonts/ARIAL.ttf"),
    "bold": os.path.join(config.RESOURCES_PATH, "fonts/ARIALBD.ttf"),
    "italic": os.path.join(config.RESOURCES_PATH, "fonts/ARIALI.ttf"),
}

FONT_NAMES = {
    "regular": "FONT_Elegant_Regular",
    "bold": "FONT_Elegant_Bold",
    "italic": "FONT_Elegant_Italic",
}

# Template dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4
FULL_COLUMN_WIDTH = PAGE_WIDTH - 1.6 * inch

# Paragraph styles with elegant typography
PARAGRAPH_STYLES = {
    "name": ParagraphStyle(
        name="elegant_name",
        fontName=FONT_NAMES["bold"],
        fontSize=16,
        textColor=COLORS["primary"],
        alignment=TA_CENTER,
        leading=18,
        spaceAfter=0,
        tracking=80,  # Letter spacing
    ),
    "title": ParagraphStyle(
        name="elegant_title",
        fontName=FONT_NAMES["italic"],
        fontSize=11,
        textColor=COLORS["secondary"],
        alignment=TA_CENTER,
        leading=14,
        spaceAfter=4,
    ),
    "contact": ParagraphStyle(
        name="elegant_contact",
        fontName=FONT_NAMES["regular"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=COLORS["secondary"],
        spaceAfter=12,
    ),
    "section": ParagraphStyle(
        name="elegant_section",
        fontName=FONT_NAMES["bold"],
        fontSize=11,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=14,
        spaceBefore=14,
        spaceAfter=8,
        textTransform="uppercase",
        tracking=80,  # Letter spacing for headings
    ),
    "objective": ParagraphStyle(
        name="elegant_objective",
        fontName=FONT_NAMES["italic"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=COLORS["black"],
        spaceAfter=10,
    ),
    "company_heading": ParagraphStyle(
        name="elegant_company_heading",
        fontName=FONT_NAMES["bold"],
        fontSize=11,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "company_title": ParagraphStyle(
        name="elegant_company_title",
        fontName=FONT_NAMES["italic"],
        fontSize=10,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "company_duration": ParagraphStyle(
        name="elegant_company_duration",
        fontName=FONT_NAMES["regular"],
        fontSize=9,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "company_location": ParagraphStyle(
        name="elegant_company_location",
        fontName=FONT_NAMES["regular"],
        fontSize=9,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "bullet_points": ParagraphStyle(
        name="elegant_bullet_points",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["black"],
        firstLineIndent=-10,
    ),
    "last_bullet_point": ParagraphStyle(
        name="elegant_last_bullet_point",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["black"],
        firstLineIndent=-10,
        spaceAfter=8,
    ),
    "education": ParagraphStyle(
        name="elegant_education",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["black"],
    ),
    "skills": ParagraphStyle(
        name="elegant_skills",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["black"],
    ),
    "skill_category": ParagraphStyle(
        name="elegant_skill_category",
        fontName=FONT_NAMES["bold"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
}


def build_elegant_resume(doc, data):
    """Build an elegant resume with refined typography ideal for graduates."""
    story = []

    # Centered header
    header_data = [
        [Paragraph(data["basic"]["name"].upper(), PARAGRAPH_STYLES["name"])],
    ]

    # If there's a current job title, add it under the name
    if data["experiences"] and not data["experiences"][0]["skip_name"]:
        current_title = data["experiences"][0]["titles"][0]["name"]
        header_data.append([Paragraph(current_title, PARAGRAPH_STYLES["title"])])

    # Create contact information with elegant formatting
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
    contact_text = " • ".join(contact_parts)  # Elegant bullet separator
    header_data.append([Paragraph(contact_text, PARAGRAPH_STYLES["contact"])])

    # Create the header table
    header = Table(
        header_data,
        colWidths=[FULL_COLUMN_WIDTH],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        ),
    )
    story.append(header)

    # Add an elegant separator line
    story.append(
        HRFlowable(
            width="40%",  # Shorter line for elegance
            thickness=1,
            color=COLORS["accent"],
            spaceBefore=4,
            spaceAfter=12,
            hAlign="CENTER",
        )
    )

    # Professional Summary section
    story.append(Paragraph("Professional Summary", PARAGRAPH_STYLES["section"]))
    story.append(Paragraph(data["objective"], PARAGRAPH_STYLES["objective"]))

    # Education section - brought higher for graduate focus
    story.append(Paragraph("Education", PARAGRAPH_STYLES["section"]))

    for edu in data["education"]:
        school = edu["school"]
        degrees = ", ".join(edu["degrees"][0]["names"])

        # Create an elegant education layout
        edu_table_data = [
            [
                Paragraph(f"<b>{school}</b>", PARAGRAPH_STYLES["company_heading"]),
                Paragraph(
                    "", PARAGRAPH_STYLES["company_duration"]
                ),  # Placeholder for alignment
            ]
        ]

        edu_table = Table(
            edu_table_data,
            colWidths=[FULL_COLUMN_WIDTH * 0.8, FULL_COLUMN_WIDTH * 0.2],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            ),
        )
        story.append(edu_table)

        # Degree information
        story.append(Paragraph(degrees, PARAGRAPH_STYLES["company_title"]))
        story.append(Spacer(1, 6))

    # Experience section
    story.append(Paragraph("Experience", PARAGRAPH_STYLES["section"]))

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
                colWidths=[FULL_COLUMN_WIDTH * 0.8, FULL_COLUMN_WIDTH * 0.2],
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
                colWidths=[FULL_COLUMN_WIDTH * 0.8, FULL_COLUMN_WIDTH * 0.2],
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
                colWidths=[FULL_COLUMN_WIDTH * 0.8, FULL_COLUMN_WIDTH * 0.2],
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

        # Job highlights with elegant bullet points
        for i, bullet_point in enumerate(job["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(job["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            story.append(Paragraph(f"• {bullet_point}", style))

    # Projects section
    story.append(Paragraph("Projects", PARAGRAPH_STYLES["section"]))

    for project in data["projects"]:
        project_name = project["name"]

        if project["show_link"]:
            raw_link = project["link"]
            clean_link = (
                raw_link.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
            )

            project_header = f"<b>{project_name}</b>: {clean_link}"
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
            colWidths=[FULL_COLUMN_WIDTH * 0.8, FULL_COLUMN_WIDTH * 0.2],
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
    story.append(Paragraph("Skills", PARAGRAPH_STYLES["section"]))

    # Group skills in pairs for a balanced layout
    skills_data = []
    skills_row = []

    for i, group in enumerate(data["skills"]):
        group_keys = list(group.keys())
        skill_type = group[group_keys[0]]
        skills_list = group[group_keys[1]]

        skill_text = f"<b>{skill_type}:</b> {', '.join(skills_list)}"
        skills_row.append(Paragraph(skill_text, PARAGRAPH_STYLES["skills"]))

        if len(skills_row) == 2 or i == len(data["skills"]) - 1:
            # Pad if we have an odd number at the end
            if len(skills_row) == 1:
                skills_row.append(Paragraph("", PARAGRAPH_STYLES["skills"]))

            skills_data.append(skills_row)
            skills_row = []

    # Create a table with skill groups in balanced columns
    if skills_data:
        skills_table = Table(
            skills_data,
            colWidths=[FULL_COLUMN_WIDTH * 0.48, FULL_COLUMN_WIDTH * 0.48],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (0, -1), 10),
                ]
            ),
        )
        story.append(skills_table)

    # Add an elegant footer line
    story.append(Spacer(1, 10))
    story.append(
        HRFlowable(
            width="40%",
            thickness=1,
            color=COLORS["accent"],
            spaceBefore=8,
            spaceAfter=0,
            hAlign="CENTER",
        )
    )

    return story
