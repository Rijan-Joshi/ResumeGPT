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

# Modern color scheme
COLORS = {
    "primary": colors.HexColor("#1976D2"),  # Blue
    "secondary": colors.HexColor("#424242"),  # Dark gray
    "accent": colors.HexColor("#2196F3"),  # Light blue
    "light": colors.HexColor("#EEEEEE"),  # Light gray
    "white": colors.white,
    "black": colors.black,
}


def generate_doc_template(name, job_data_location):
    """Generate and return a SimpleDocTemplate for a modern two-column resume PDF."""
    author_name_formatted = name.replace(" ", "_") + "_modern_resume_try1"
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
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        title=f"{author_name_formatted}",
        author=name,
    )
    return (doc, pdf_location)


# Define fonts - different from other templates
FONT_PATHS = {
    "regular": os.path.join(config.RESOURCES_PATH, "fonts/ARIAL.ttf"),
    "bold": os.path.join(config.RESOURCES_PATH, "fonts/ARIALBD.ttf"),
    "italic": os.path.join(config.RESOURCES_PATH, "fonts/ARIALI.ttf"),
}

FONT_NAMES = {
    "regular": "FONT_Modern_Regular",
    "bold": "FONT_Modern_Bold",
    "italic": "FONT_Modern_Italic",
}

# Template dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4
MAIN_COLUMN_WIDTH = PAGE_WIDTH * 0.68 - inch
SIDE_COLUMN_WIDTH = PAGE_WIDTH * 0.32 - inch
FULL_COLUMN_WIDTH = PAGE_WIDTH - inch

# Paragraph styles with modern fonts and spacing
PARAGRAPH_STYLES = {
    "name": ParagraphStyle(
        name="modern_name",
        fontName=FONT_NAMES["bold"],
        fontSize=18,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=22,
        spaceBefore=0,
        spaceAfter=2,
    ),
    "title": ParagraphStyle(
        name="modern_title",
        fontName=FONT_NAMES["italic"],
        fontSize=11,
        textColor=COLORS["secondary"],
        alignment=TA_LEFT,
        leading=14,
        spaceAfter=10,
    ),
    "contact": ParagraphStyle(
        name="modern_contact",
        fontName=FONT_NAMES["regular"],
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=COLORS["secondary"],
        spaceAfter=6,
    ),
    "section": ParagraphStyle(
        name="modern_section",
        fontName=FONT_NAMES["bold"],
        fontSize=12,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=14,
        spaceBefore=10,
        spaceAfter=6,
        textTransform="uppercase",
    ),
    "side_section": ParagraphStyle(
        name="modern_side_section",
        fontName=FONT_NAMES["bold"],
        fontSize=11,
        textColor=COLORS["white"],
        alignment=TA_LEFT,
        leading=14,
        spaceBefore=8,
        spaceAfter=6,
        textTransform="uppercase",
        backColor=COLORS["primary"],
        borderPadding=(3, 0, 3, 5),
    ),
    "objective": ParagraphStyle(
        name="modern_objective",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=COLORS["secondary"],
        spaceAfter=10,
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
        fontName=FONT_NAMES["bold"],
        fontSize=9,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["primary"],
    ),
    "company_location": ParagraphStyle(
        name="modern_company_location",
        fontName=FONT_NAMES["regular"],
        fontSize=9,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "bullet_points": ParagraphStyle(
        name="modern_bullet_points",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=9.5,
        leading=13,
        alignment=TA_LEFT,
        textColor=COLORS["secondary"],
        firstLineIndent=-10,
    ),
    "last_bullet_point": ParagraphStyle(
        name="modern_last_bullet_point",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=9.5,
        leading=13,
        alignment=TA_LEFT,
        textColor=COLORS["secondary"],
        firstLineIndent=-10,
        spaceAfter=8,
    ),
    "education": ParagraphStyle(
        name="modern_education",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["secondary"],
    ),
    "skills": ParagraphStyle(
        name="modern_skills",
        fontName=FONT_NAMES["regular"],
        fontSize=9.5,
        leading=13,
        textColor=COLORS["secondary"],
    ),
    "skill_category": ParagraphStyle(
        name="modern_skill_category",
        fontName=FONT_NAMES["bold"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "side_content": ParagraphStyle(
        name="modern_side_content",
        fontName=FONT_NAMES["regular"],
        fontSize=9,
        leading=13,
        textColor=COLORS["secondary"],
        spaceBefore=2,
        spaceAfter=8,
    ),
}


def build_modern_resume(doc, data):
    """Build a modern two-column resume that's still ATS-friendly."""
    story = []

    # Main table to create a two-column layout
    # We'll have a main column for experience and a side column for skills/education
    main_column_content = []
    side_column_content = []

    # SIDE COLUMN CONTENT
    # Contact Information
    contact_parts = []
    contact_parts.append(f"<b>Email:</b> {data['basic']['email']}")
    contact_parts.append(f"<b>Phone:</b> {data['basic']['phone']}")

    # Add address
    contact_parts.append(f"<b>Address:</b> {data['basic']['address']}")

    # Add websites
    for website in data["basic"]["websites"]:
        website_clean = (
            website.replace("https://", "").replace("http://", "").replace("www.", "")
        )
        contact_parts.append(f"<b>Web:</b> {website_clean}")

    # Contact section
    side_column_content.append(Paragraph("CONTACT", PARAGRAPH_STYLES["side_section"]))
    for contact_item in contact_parts:
        side_column_content.append(
            Paragraph(contact_item, PARAGRAPH_STYLES["side_content"])
        )

    # Skills section
    side_column_content.append(Paragraph("SKILLS", PARAGRAPH_STYLES["side_section"]))
    for group in data["skills"]:
        group_keys = list(group.keys())
        skill_type = group[group_keys[0]]
        skills_list = group[group_keys[1]]

        skill_text = f"<b>{skill_type}:</b><br/>{', '.join(skills_list)}"
        side_column_content.append(
            Paragraph(skill_text, PARAGRAPH_STYLES["side_content"])
        )

    # Education section
    side_column_content.append(Paragraph("EDUCATION", PARAGRAPH_STYLES["side_section"]))
    for edu in data["education"]:
        school = edu["school"]
        degrees = ", ".join(edu["degrees"][0]["names"])

        education_text = f"<b>{school}</b><br/>{degrees}"
        side_column_content.append(
            Paragraph(education_text, PARAGRAPH_STYLES["side_content"])
        )

    # MAIN COLUMN CONTENT
    # Header with name
    main_column_content.append(
        Paragraph(data["basic"]["name"], PARAGRAPH_STYLES["name"])
    )

    # If there's a current job title, add it under the name
    if data["experiences"] and not data["experiences"][0]["skip_name"]:
        current_title = data["experiences"][0]["titles"][0]["name"]
        main_column_content.append(Paragraph(current_title, PARAGRAPH_STYLES["title"]))

    # Add a separator line
    main_column_content.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=COLORS["primary"],
            spaceBefore=0,
            spaceAfter=8,
            hAlign="LEFT",
        )
    )

    # Professional Summary
    main_column_content.append(
        Paragraph("PROFESSIONAL SUMMARY", PARAGRAPH_STYLES["section"])
    )
    main_column_content.append(
        Paragraph(data["objective"], PARAGRAPH_STYLES["objective"])
    )

    # Work Experience section
    main_column_content.append(
        Paragraph("WORK EXPERIENCE", PARAGRAPH_STYLES["section"])
    )

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
                colWidths=[MAIN_COLUMN_WIDTH * 0.7, MAIN_COLUMN_WIDTH * 0.3],
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
            main_column_content.append(job_table)

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
                colWidths=[MAIN_COLUMN_WIDTH * 0.7, MAIN_COLUMN_WIDTH * 0.3],
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
            main_column_content.append(title_table)
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
                colWidths=[MAIN_COLUMN_WIDTH * 0.7, MAIN_COLUMN_WIDTH * 0.3],
                style=TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                ),
            )
            main_column_content.append(job_table)

        # Job highlights (bullet points)
        for i, bullet_point in enumerate(job["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(job["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            main_column_content.append(Paragraph(f"• {bullet_point}", style))

    # Projects section
    main_column_content.append(Paragraph("PROJECTS", PARAGRAPH_STYLES["section"]))

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
            colWidths=[MAIN_COLUMN_WIDTH * 0.7, MAIN_COLUMN_WIDTH * 0.3],
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
        main_column_content.append(project_table)

        # Project highlights (bullet points)
        for i, bullet_point in enumerate(project["highlights"]):
            bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
            style = (
                PARAGRAPH_STYLES["last_bullet_point"]
                if i == len(project["highlights"]) - 1
                else PARAGRAPH_STYLES["bullet_points"]
            )
            main_column_content.append(Paragraph(f"• {bullet_point}", style))

    # Create the main two-column layout table
    resume_table_data = [[main_column_content, side_column_content]]
    resume_table = Table(
        resume_table_data,
        colWidths=[MAIN_COLUMN_WIDTH, SIDE_COLUMN_WIDTH],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 10),
                ("LEFTPADDING", (1, 0), (1, 0), 10),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("BACKGROUND", (1, 0), (1, 0), COLORS["light"]),
            ]
        ),
    )

    story.append(resume_table)
    return story
