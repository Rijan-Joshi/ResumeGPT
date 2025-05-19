import configparser
import json
import os
import random
import config
import utils
import subprocess
import yaml

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    HRFlowable,
)
from . import (
    resume_pdf_styles as classic_template,
    # resume_modern_template as modern_template,
    modern_template,
    resume_modern_template as modern_template2,
    chronological_template,
    professional_template,
    elegant_template,
    minimal_template,
    technical_template,
    try1,
    template2,
    professional_template2,
    professional_template3,
    technical_expert_template,
)


class ResumePDFGenerator:
    """
    A class to generate a resume PDF from JSON data using the ReportLab library.
    """

    TEMPLATES = {
        "classic": classic_template,
        "modern": modern_template,
        "chronological": chronological_template,
        "modern2": modern_template2,
        "professional": professional_template,
        "elegant": elegant_template,
        "minimal": minimal_template,
        "technical": technical_template,
        "try1": try1,
        "template2": template2,
        "professional2": professional_template2,
        "professional3": professional_template3,
        "technical_expert": technical_expert_template,
    }

    def __init__(self, template_name="classic"):
        """
        Initialize the ResumePDFGenerator by registering fonts.
        """
        self.template_name = template_name
        self.template = self.TEMPLATES.get(template_name, classic_template)
        self._register_fonts()

    def _register_fonts(self):
        """
        Register fonts for use in the PDF.
        """
        for style, path in self.template.FONT_PATHS.items():
            pdfmetrics.registerFont(
                ttfonts.TTFont(self.template.FONT_NAMES[style], path)
            )

    def _append_section_table_style(self, table_styles, row_index):
        """
        Append styles for section headers in the table.

        Args:
            table_styles (list): List of table styles to be extended.
            row_index (int): The current row index in the table.
        """
        table_styles.extend(
            [
                ("TOPPADDING", (0, row_index), (1, row_index), 5),
                ("BOTTOMPADDING", (0, row_index), (1, row_index), 2),
                ("LINEBELOW", (0, row_index), (-1, row_index), 0.1, colors.black),
            ]
        )

    def _add_table_row(
        self,
        table_data,
        table_styles,
        row_index,
        content_style_map,
        span=False,
        padding=None,
        bullet_point=None,
    ):
        """
        Add a row to the table data and update the table styles.

        Args:
            table_data (list): The table data to be extended.
            table_styles (list): The table styles to be extended.
            row_index (int): The current row index in the table.
            content_style_map (list of tuples): A list of tuples where each tuple contains content and its corresponding style.
            span (bool, optional): Whether the row should span across columns. Defaults to False.
            padding (tuple, optional): The top and bottom padding for the row. Defaults to (1, 1).
            bullet_point (str, optional): The bullet point to prepend to the content.
            spacer_height (int, optional): The height of the spacer to add after the row. Defaults to None.
        """
        if padding is None:
            padding = self.template.DEFAULT_PADDING

        if bullet_point:
            table_data.append(
                [
                    Paragraph(content, bulletText=bullet_point, style=style)
                    for content, style in content_style_map
                ]
            )
        else:
            table_data.append(
                [Paragraph(content, style) for content, style in content_style_map]
            )
        table_styles.extend(
            [
                ("BOTTOMPADDING", (0, row_index), (-1, row_index), padding[0]),
                ("TOPPADDING", (0, row_index), (-1, row_index), padding[1]),
            ]
        )
        if span:
            table_styles.append(("SPAN", (0, row_index), (1, row_index)))

        row_index += 1

        return row_index

    def add_experiences(self, table_data, table_styles, row_index, experiences):
        """
        Add experiences section to the resume.

        Args:
            table_data (list): The table data to be extended.
            table_styles (list): The table styles to be extended.
            row_index (int): The current row index in the table.
            experiences (list): The list of experiences to be added.
        """
        row_index = self._add_table_row(
            table_data=table_data,
            table_styles=table_styles,
            row_index=row_index,
            content_style_map=[
                ("Experience", self.template.PARAGRAPH_STYLES["section"])
            ],
            span=True,
        )
        self._append_section_table_style(table_styles, row_index - 1)

        for idx, job in enumerate(experiences):
            # Create a duration string from startdate and enddate
            duration = f"{job['titles'][0]['startdate']}-{job['titles'][0]['enddate']}"
            if job["skip_name"]:
                row_index = self._add_table_row(
                    table_data=table_data,
                    table_styles=table_styles,
                    row_index=row_index,
                    content_style_map=[
                        (
                            job["titles"][0]["name"],
                            self.template.PARAGRAPH_STYLES["company_title"],
                        ),
                        (
                            duration,
                            self.template.PARAGRAPH_STYLES["company_duration"],
                        ),
                    ],
                )

            else:
                row_index = self._add_table_row(
                    table_data=table_data,
                    table_styles=table_styles,
                    row_index=row_index,
                    content_style_map=[
                        (
                            job["company"],
                            self.template.PARAGRAPH_STYLES["company_heading"],
                        ),
                        (
                            duration,
                            self.template.PARAGRAPH_STYLES["company_duration"],
                        ),
                    ],
                )

                row_index = self._add_table_row(
                    table_data=table_data,
                    table_styles=table_styles,
                    row_index=row_index,
                    content_style_map=[
                        (
                            job["titles"][0]["name"],
                            self.template.PARAGRAPH_STYLES["company_title"],
                        ),
                        (
                            job["location"],
                            self.template.PARAGRAPH_STYLES["company_location"],
                        ),
                    ],
                )

            for i, bullet_point in enumerate(job["highlights"]):
                bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
                style = (
                    self.template.PARAGRAPH_STYLES["last_bullet_point"]
                    if i == len(job["highlights"]) - 1
                    else self.template.PARAGRAPH_STYLES["bullet_points"]
                )
                padding = (0, 1)
                if i == len(job["highlights"]) - 1:
                    padding = (5, 1)
                row_index = self._add_table_row(
                    table_data=table_data,
                    table_styles=table_styles,
                    bullet_point="•",
                    row_index=row_index,
                    content_style_map=[
                        (
                            bullet_point,
                            style,
                        )
                    ],
                    span=True,
                    padding=padding,
                )

        return row_index

    def add_projects(self, table_data, table_styles, row_index, projects):
        """
        Add projects section to the resume.

        Args:
            table_data (list): The table data to be extended.
            table_styles (list): The table styles to be extended.
            row_index (int): The current row index in the table.
            projects (list): The list of projects to be added.
        """
        row_index = self._add_table_row(
            table_data=table_data,
            table_styles=table_styles,
            row_index=row_index,
            content_style_map=[("Projects", self.template.PARAGRAPH_STYLES["section"])],
            span=True,
        )
        self._append_section_table_style(table_styles, row_index - 1)

        for idx, project in enumerate(projects):
            project_name = project["name"]
            raw_link = project["link"]
            clean_link = (
                raw_link.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
            )
            if project["show_link"]:
                if project["hyperlink"]:
                    hyperlink_text = '<a href="%s">%s</a>' % (raw_link, clean_link)
                    link_style = self.template.PARAGRAPH_STYLES["link"]
                else:
                    hyperlink_text = clean_link
                    link_style = self.template.PARAGRAPH_STYLES["link-no-hyperlink"]
                heading_style = self.template.PARAGRAPH_STYLES["company_heading"]
                combined_style = ParagraphStyle(
                    "combined_project_style",
                    parent=heading_style,
                    allowWidows=0,
                    allowOrphans=0,
                )
                link_color_hex = "#" + link_style.textColor.hexval()[2:]
                paragraph_text = (
                    f'<font name="{heading_style.fontName}" size="{heading_style.fontSize}">'
                    f"{project_name}: </font>"
                    f'<font name="{link_style.fontName}" size="{link_style.fontSize}" color="{link_color_hex}">'
                    f"{hyperlink_text}</font>"
                )

                row_index = self._add_table_row(
                    table_data=table_data,
                    table_styles=table_styles,
                    row_index=row_index,
                    content_style_map=[
                        (paragraph_text, combined_style),
                        (
                            project["date"],
                            self.template.PARAGRAPH_STYLES["company_duration"],
                        ),
                    ],
                )
            else:
                row_index = self._add_table_row(
                    table_data=table_data,
                    table_styles=table_styles,
                    row_index=row_index,
                    content_style_map=[
                        (
                            project_name,
                            self.template.PARAGRAPH_STYLES["company_heading"],
                        ),
                        (
                            project["date"],
                            self.template.PARAGRAPH_STYLES["company_duration"],
                        ),
                    ],
                )

            for i, bullet_point in enumerate(project["highlights"]):
                bullet_point = bullet_point.replace("'", "").replace('"', "").strip()
                style = (
                    self.template.PARAGRAPH_STYLES["last_bullet_point"]
                    if i == len(project["highlights"]) - 1
                    else self.template.PARAGRAPH_STYLES["bullet_points"]
                )
                padding = (0, 1)
                if i == len(project["highlights"]) - 1:
                    padding = (5, 1)
                row_index = self._add_table_row(
                    table_data=table_data,
                    table_styles=table_styles,
                    bullet_point="•",
                    row_index=row_index,
                    content_style_map=[
                        (
                            bullet_point,
                            style,
                        )
                    ],
                    span=True,
                    padding=padding,
                )

        return row_index

    def add_education(self, table_data, table_styles, row_index, education):
        """
        Add education section to the resume.

        Args:
            table_data (list): The table data to be extended.
            table_styles (list): The table styles to be extended.
            row_index (int): The current row index in the table.
            education (list): The list of education entries to be added.
        """
        row_index = self._add_table_row(
            table_data=table_data,
            table_styles=table_styles,
            row_index=row_index,
            content_style_map=[
                ("Education", self.template.PARAGRAPH_STYLES["section"])
            ],
            span=True,
        )
        self._append_section_table_style(table_styles, row_index - 1)

        for edu in education:
            degrees = ", ".join(edu["degrees"][0]["names"])
            row_index = self._add_table_row(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                content_style_map=[
                    (
                        f"<font name='{self.template.FONT_NAMES['bold']}'>{edu['school']}</font>, {degrees}",
                        self.template.PARAGRAPH_STYLES["education"],
                    )
                ],
                span=True,
            )
        return row_index

    def add_skills(self, table_data, table_styles, row_index, skills):
        """
        Add skills section to the resume.

        Args:
            table_data (list): The table data to be extended.
            table_styles (list): The table styles to be extended.
            row_index (int): The current row index in the table.
            skills (list): The list of skills to be added.
        """
        row_index = self._add_table_row(
            table_data=table_data,
            table_styles=table_styles,
            row_index=row_index,
            content_style_map=[("Skills", self.template.PARAGRAPH_STYLES["section"])],
            span=True,
        )
        self._append_section_table_style(table_styles, row_index - 1)

        for group in skills:
            group_keys = list(group.keys())
            skill_type = group[group_keys[0]]
            skills_list = group[group_keys[1]]
            skills_str = ", ".join(skills_list)
            formatted_skills = f"<font name='{self.template.FONT_NAMES['bold']}'>{skill_type}</font>: {skills_str}"
            row_index = self._add_table_row(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                content_style_map=[
                    (formatted_skills, self.template.PARAGRAPH_STYLES["skills"])
                ],
                span=True,
                padding=(2, 2),
            )
        return row_index

    def generate_resume(self, job_data_location, data):
        """
        Generate a resume PDF from JSON data.

        Args:
            job_data_location (str): The path where the PDF will be saved.
            data (dict): The JSON data containing resume information.
        """
        email = data["basic"]["email"]
        name = data["basic"]["name"]
        phone = data["basic"]["phone"]

        info = f"{email} | {phone}"

        def clean_url(url):
            return (
                url.replace("https://", "").replace("http://", "").replace("www.", "")
            )

        for website in data["basic"]["websites"]:
            info += f" | {clean_url(website)}"

        address = data["basic"]["address"]
        info += f" | {address}"
        doc, pdf_location = self.template.generate_doc_template(name, job_data_location)

        if self.template_name == "modern" and hasattr(
            self.template, "build_modern_resume"
        ):
            story = self.template.build_modern_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "chronological" and hasattr(
            self.template, "build_timeline_resume"
        ):
            story = self.template.build_timeline_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "professional" and hasattr(
            self.template, "build_professional_resume"
        ):
            story = self.template.build_professional_resume(doc, data)
            doc.build(story)
            return pdf_location

        elif self.template_name == "elegant" and hasattr(
            self.template, "build_elegant_resume"
        ):
            story = self.template.build_elegant_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "minimal" and hasattr(
            self.template, "build_minimal_ats_resume"
        ):
            story = self.template.build_minimal_ats_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "technical" and hasattr(
            self.template, "build_technical_resume"
        ):
            story = self.template.build_technical_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "try1" and hasattr(
            self.template, "build_modern_resume"
        ):
            story = self.template.build_modern_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "template2" and hasattr(
            self.template, "build_template_resume"
        ):
            story = self.template.build_template_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "professional2" and hasattr(
            self.template, "build_professional_ats_resume"
        ):
            story = self.template.build_professional_ats_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "professional3" and hasattr(
            self.template, "build_professional_ats_resume"
        ):
            story = self.template.build_professional_ats_resume(doc, data)
            doc.build(story)
            return pdf_location
        elif self.template_name == "technical_expert" and hasattr(
            self.template, "build_technical_expert_resume"
        ):
            story = self.template.build_technical_expert_resume(doc, data)
            doc.build(story)
            return pdf_location
        else:
            table_data = []
            table_styles = []
            row_index = 0

            if data.get("debug", False):
                table_styles.append(self.template.DEBUG_STYLE)

            table_styles.extend(self.template.DOCUMENT_ALIGNMENT)

            # Add name and contact information
            row_index = self._add_table_row(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                content_style_map=[(name, self.template.PARAGRAPH_STYLES["name"])],
                span=True,
            )

            row_index = self._add_table_row(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                content_style_map=[
                    (
                        info,
                        self.template.PARAGRAPH_STYLES["contact"],
                    )
                ],
                span=True,
            )

            # Add objective
            row_index = self._add_table_row(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                content_style_map=[
                    ("Objective", self.template.PARAGRAPH_STYLES["section"])
                ],
                span=True,
            )
            self._append_section_table_style(table_styles, row_index - 1)

            row_index = self._add_table_row(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                content_style_map=[
                    (data["objective"], self.template.PARAGRAPH_STYLES["objective"])
                ],
                span=True,
            )

            # Add experience
            row_index = self.add_experiences(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                experiences=data["experiences"],
            )
            # Add projects
            row_index = self.add_projects(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                projects=data["projects"],
            )

            # Add education
            row_index = self.add_education(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                education=data["education"],
            )

            # Add skills
            row_index = self.add_skills(
                table_data=table_data,
                table_styles=table_styles,
                row_index=row_index,
                skills=data["skills"],
            )

            left_col_width = self.template.FULL_COLUMN_WIDTH * 0.75
            right_col_width = self.template.FULL_COLUMN_WIDTH * 0.25

            # For modern template, adjust column widths
            if self.template_name == "modern":
                left_col_width = self.template.FULL_COLUMN_WIDTH * 0.7
                right_col_width = self.template.FULL_COLUMN_WIDTH * 0.3

            table = Table(
                table_data,
                colWidths=[left_col_width, right_col_width],
                spaceBefore=0,
                spaceAfter=0,
            )
            table.setStyle(TableStyle(table_styles))

            doc.build([table])
            return pdf_location

    def generate_pdf_from_resume_yaml(
        self, yaml_path, job_data_location, template_name=None
    ):
        """
        Generate a resume PDF from YAML data.

        Args:
            yaml_path (str): The path to the YAML file containing resume information.
            job_data_location (str): The path where the PDF will be saved.
        """
        if template_name and template_name in self.TEMPLATES:
            old_template = self.template_name
            self.template_name = template_name
            self.template = self.TEMPLATES[template_name]
            self._register_fonts()

            # Generate the resume
            result = self.generate_resume(
                job_data_location, utils.read_yaml(filename=yaml_path)
            )

            # Restore original template
            self.template_name = old_template
            self.template = self.TEMPLATES[old_template]
            self._register_fonts()

            return result
        else:
            # Use current template
            return self.generate_resume(
                job_data_location, utils.read_yaml(filename=yaml_path)
            )
