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

# Timeline color scheme
COLORS = {
    "primary": colors.HexColor("#003366"),  # Dark blue
    "accent": colors.HexColor("#990000"),  # Dark red
    "timeline": colors.HexColor("#336699"),  # Medium blue
    "secondary": colors.HexColor("#666666"),  # Dark gray
}


def generate_doc_template(name, job_data_location):
    """
    Generate and return a SimpleDocTemplate for a timeline-focused resume PDF.
    """
    author_name_formatted = name.replace(" ", "_") + "_timeline_resume"
    pdf_location = os.path.join(job_data_location, f"{author_name_formatted}.pdf")
    doc = SimpleDocTemplate(
        pdf_location,
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        title=f"{author_name_formatted}",
        author=name,
    )
    return (doc, pdf_location)


# Define styles for timeline template
FONT_PATHS = {
    "regular": os.path.join(config.RESOURCES_PATH, "fonts/calibri.ttf"),
    "bold": os.path.join(config.RESOURCES_PATH, "fonts/calibrib.ttf"),
    "italic": os.path.join(config.RESOURCES_PATH, "fonts/calibrii.ttf"),
}

FONT_NAMES = {
    "regular": "FONT_Timeline_Regular",
    "bold": "FONT_Timeline_Bold",
    "italic": "FONT_Timeline_Italic",
}

DEFAULT_PADDING = (2, 2)
DOCUMENT_ALIGNMENT = []  # We'll handle alignment differently for this template
DEBUG_STYLE = ("GRID", (0, 0), (-1, -1), 0, colors.black)

PAGE_WIDTH, PAGE_HEIGHT = A4
FULL_COLUMN_WIDTH = PAGE_WIDTH - 1.5 * inch

# Paragraph styles
PARAGRAPH_STYLES = {
    "name": ParagraphStyle(
        name="timeline_name",
        fontName=FONT_NAMES["bold"],
        fontSize=18,
        textColor=COLORS["primary"],
        alignment=TA_CENTER,
        leading=22,
        spaceAfter=4,
    ),
    "title": ParagraphStyle(
        name="timeline_title",
        fontName=FONT_NAMES["italic"],
        fontSize=12,
        textColor=COLORS["secondary"],
        alignment=TA_CENTER,
        leading=14,
        spaceAfter=6,
    ),
    "contact": ParagraphStyle(
        name="timeline_contact",
        fontName=FONT_NAMES["regular"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=COLORS["secondary"],
        spaceAfter=15,
    ),
    "section": ParagraphStyle(
        name="timeline_section",
        fontName=FONT_NAMES["bold"],
        fontSize=14,
        textColor=COLORS["primary"],
        alignment=TA_LEFT,
        leading=18,
        spaceBefore=10,
        spaceAfter=10,
    ),
    "objective": ParagraphStyle(
        name="timeline_objective",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=COLORS["secondary"],
        spaceAfter=10,
    ),
    "year": ParagraphStyle(
        name="timeline_year",
        fontName=FONT_NAMES["bold"],
        fontSize=12,
        textColor=COLORS["timeline"],
        alignment=TA_LEFT,
        leading=14,
    ),
    "company_heading": ParagraphStyle(
        name="timeline_company_heading",
        fontName=FONT_NAMES["bold"],
        fontSize=11,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "company_title": ParagraphStyle(
        name="timeline_company_title",
        fontName=FONT_NAMES["italic"],
        fontSize=10,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "company_duration": ParagraphStyle(
        name="timeline_company_duration",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "company_location": ParagraphStyle(
        name="timeline_company_location",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        alignment=TA_RIGHT,
        leading=12,
        textColor=COLORS["secondary"],
    ),
    "bullet_points": ParagraphStyle(
        name="timeline_bullet_points",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["secondary"],
        firstLineIndent=-10,
    ),
    "last_bullet_point": ParagraphStyle(
        name="timeline_last_bullet_point",
        leftIndent=15,
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        textColor=COLORS["secondary"],
        firstLineIndent=-10,
        spaceAfter=8,
    ),
    "education": ParagraphStyle(
        name="timeline_education",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["secondary"],
        leftIndent=15,
    ),
    "skills": ParagraphStyle(
        name="timeline_skills",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["secondary"],
    ),
    "skill_category": ParagraphStyle(
        name="timeline_skill_category",
        fontName=FONT_NAMES["bold"],
        fontSize=10,
        leading=14,
        textColor=COLORS["primary"],
    ),
    "link": ParagraphStyle(
        name="timeline_link",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        textColor=COLORS["accent"],
        underline=True,
    ),
    "link-no-hyperlink": ParagraphStyle(
        name="timeline_link_no_hyperlink",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        textColor=COLORS["secondary"],
    ),
    "normal": ParagraphStyle(
        name="timeline_normal",
        fontName=FONT_NAMES["regular"],
        fontSize=10,
        leading=14,
        textColor=COLORS["secondary"],
    ),
    "space": ParagraphStyle(
        name="timeline_space",
        fontName=FONT_NAMES["regular"],
        fontSize=0,
        leading=0,
    ),
}


def build_timeline_resume(doc, data):
    """
    Build a resume with a focus on chronology and timeline visualization.
    This function should replace the standard build process in the generator.
    """
    story = []

    # Calculate content width
    content_width = PAGE_WIDTH - doc.leftMargin - doc.rightMargin

    # Header with name, title, and contact info
    story.append(Paragraph(data["basic"]["name"].upper(), PARAGRAPH_STYLES["name"]))

    # If there's a current job title, add it under the name
    if data["experiences"] and not data["experiences"][0]["skip_name"]:
        current_title = data["experiences"][0]["titles"][0]["name"]
        story.append(Paragraph(current_title, PARAGRAPH_STYLES["title"]))

    # Contact information on one line
    email = data["basic"]["email"]
    phone = data["basic"]["phone"]
    contact_parts = [email, phone]

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
    story.append(Paragraph(contact_text, PARAGRAPH_STYLES["contact"]))

    # Objective section
    story.append(Paragraph("PROFESSIONAL SUMMARY", PARAGRAPH_STYLES["section"]))
    story.append(Paragraph(data["objective"], PARAGRAPH_STYLES["objective"]))

    # Experience section
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", PARAGRAPH_STYLES["section"]))

    # Group experiences by year for the timeline effect
    experiences_by_year = {}

    for job in data["experiences"]:
        # Get the start year
        start_year = str(job["titles"][0]["startdate"]).split("-")[0]
        if not start_year in experiences_by_year:
            experiences_by_year[start_year] = []

        experiences_by_year[start_year].append(job)

    # Sort years in reverse chronological order
    sorted_years = sorted(experiences_by_year.keys(), reverse=True)

    # Create timeline-style layout
    for year in sorted_years:
        # Year marker
        year_bullet = Table(
            [
                [
                    Paragraph(year, PARAGRAPH_STYLES["year"]),
                    HRFlowable(
                        width=content_width * 0.75,
                        thickness=1,
                        color=COLORS["timeline"],
                        spaceBefore=8,
                        spaceAfter=5,
                    ),
                ]
            ],
            colWidths=[content_width * 0.1, content_width * 0.9],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (0, -1), 0),
                    ("RIGHTPADDING", (0, 0), (0, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            ),
        )
        story.append(year_bullet)

        # Jobs for this year
        for job in experiences_by_year[year]:
            # Create duration string
            duration = f"{job['titles'][0]['startdate']}-{job['titles'][0]['enddate']}"

            # Job details table
            job_details = []

            if not job["skip_name"]:
                # Company and duration
                company_row = Table(
                    [
                        [
                            Paragraph(
                                job["company"], PARAGRAPH_STYLES["company_heading"]
                            ),
                            Paragraph(duration, PARAGRAPH_STYLES["company_duration"]),
                        ]
                    ],
                    colWidths=[content_width * 0.7, content_width * 0.3],
                    style=TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (0, 0), 15),  # Indent from timeline
                            ("RIGHTPADDING", (0, 0), (0, 0), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                        ]
                    ),
                )
                job_details.append(company_row)

                # Job title and location
                title_row = Table(
                    [
                        [
                            Paragraph(
                                job["titles"][0]["name"],
                                PARAGRAPH_STYLES["company_title"],
                            ),
                            Paragraph(
                                job["location"], PARAGRAPH_STYLES["company_location"]
                            ),
                        ]
                    ],
                    colWidths=[content_width * 0.7, content_width * 0.3],
                    style=TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (0, 0), 15),  # Indent from timeline
                            ("RIGHTPADDING", (0, 0), (0, 0), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    ),
                )
                job_details.append(title_row)
            else:
                # Just title and duration
                title_row = Table(
                    [
                        [
                            Paragraph(
                                job["titles"][0]["name"],
                                PARAGRAPH_STYLES["company_title"],
                            ),
                            Paragraph(duration, PARAGRAPH_STYLES["company_duration"]),
                        ]
                    ],
                    colWidths=[content_width * 0.7, content_width * 0.3],
                    style=TableStyle(
                        [
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (0, 0), 15),  # Indent from timeline
                            ("RIGHTPADDING", (0, 0), (0, 0), 0),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    ),
                )
                job_details.append(title_row)

            for detail in job_details:
                story.append(detail)

            # Job highlights (bullet points)
            for i, bullet_point in enumerate(job["highlights"]):
                bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
                style = (
                    PARAGRAPH_STYLES["last_bullet_point"]
                    if i == len(job["highlights"]) - 1
                    else PARAGRAPH_STYLES["bullet_points"]
                )

                # Give extra left indent to align with the job title
                bullet_para = Paragraph(f"• {bullet_point}", style)
                story.append(bullet_para)

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

            if project["hyperlink"]:
                link_text = f"<a href='{raw_link}' color='#{COLORS['accent'].hexval()[2:]}'>{clean_link}</a>"
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
            colWidths=[content_width * 0.7, content_width * 0.3],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
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

    # Skills section in a grid layout
    story.append(Paragraph("SKILLS & EXPERTISE", PARAGRAPH_STYLES["section"]))

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
    skills_table = Table(
        skills_data,
        colWidths=[content_width * 0.48, content_width * 0.48],
        style=TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]
        ),
    )
    story.append(skills_table)

    # Education section
    story.append(Paragraph("EDUCATION", PARAGRAPH_STYLES["section"]))

    for edu in data["education"]:
        school = edu["school"]
        degrees = ", ".join(edu["degrees"][0]["names"])

        education_text = f"<b>{school}</b>, {degrees}"
        story.append(Paragraph(education_text, PARAGRAPH_STYLES["education"]))

    return story
