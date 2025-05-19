from pdf_generation.resume_pdf_generator import ResumePDFGenerator
import utils
import os

os.makedirs("resume", exist_ok=True)

template_keys = [
    "classic",
    "modern",
    "chronological",
    "modern2",
    "professional",
    "elegant",
    "minimal",
    "technical",
    "template2",
    "professional2",
    "professional3",
]

for template_name in template_keys:
    pdf_generator = ResumePDFGenerator(template_name=template_name)
    pdf_generator.generate_resume(
        "resume",
        utils.read_yaml(
            filename="data/Website_Toolbox_Sr._Software_Engineer/resume.yaml"
        ),
    )
