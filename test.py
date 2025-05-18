from services import ResumeImprover
from pdf_generation.resume_pdf_generator import ResumePDFGenerator
import utils
import warnings

warnings.filterwarnings("ignore", message="Received a Pydantic BaseModel V1 schema")

url = "https://www.linkedin.com/jobs/view/4097292294/"
resume_improver = ResumeImprover(url)
resume_improver.create_draft_tailored_resume()


pdf_generator = ResumePDFGenerator()
pdf_generator.generate_resume(
    "resume",
    utils.read_yaml(filename="data/Website_Toolbox_Sr._Software_Engineer/resume.yaml"),
)
