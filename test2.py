from pdf_generation.resume_pdf_generator import ResumePDFGenerator
import utils
import os

os.makedirs("resume", exist_ok=True)


pdf_generator = ResumePDFGenerator(template_name="modern")
pdf_generator.generate_resume(
    "resume",
    utils.read_yaml(filename="data/Website_Toolbox_Sr._Software_Engineer/resume.yaml"),
)
