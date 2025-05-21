from services import ResumeImprover
from pdf_generation.resume_pdf_generator import ResumePDFGenerator
import utils
import warnings

warnings.filterwarnings("ignore", message="Received a Pydantic BaseModel V1 schema")

url = "https://www.linkedin.com/jobs/view/4097292294/"

job_description = """
ats_keywords:
- Java
- Spring
- Asp.net
- C#
- Oracle
- MS-SQL
- MariaDB
- Mysql
- Postgre
- Responsive Web development
- API development
- Kakao
- Naver
- Google
- Apple
- Mobile authentication
- Web payment integration
- Batch development
- React
- Vue.js
company: Website Toolbox
duties:
- Writing well-designed, testable, and efficient code.
- Gathering and evaluating user feedback.
- Working as part of a dynamic team to deliver winning products.
- Providing code documentation and other inputs to technical documents.
- Supporting continuous improvement by investigating alternatives and new technologies
  and presenting these for architectural review.
- Troubleshooting and debugging to optimize performance.
is_fully_remote: true
job_summary: Website Toolbox is seeking a Sr. Software Engineer to join our team in
  Nepal. This role involves writing well-designed, testable, and efficient code, gathering
  user feedback, and working collaboratively to deliver innovative products. The position
  offers a fully remote work environment with fixed weekends off.
job_title: Sr. Software Engineer
non_technical_skills:
- User feedback evaluation
- Team collaboration
- Troubleshooting
- Debugging
- Continuous improvement
qualifications:
- Experienced in responsive Web development and worked with Rijan.
- Experienced in API development.
- Experienced in integration of simplified sign-up/login systems (Kakao, Naver, Google,
  Apple).
- Experienced in integration of mobile authentication during sign-up (e.g., KMS).
- Experienced in web payment integration (e.g., Toss).
- Experienced in batch development using console programs.
- Experienced in batch development utilizing D job scheduling.
- Experienced in stored procedures.
- Proficiency in React or Vue.js for front-end development.
- Proficiency in IDE and development environment setup.
salary: $11,988.00/yr - $12,000.00/yr
team: null
technical_skills:
- Java
- Spring Framework
- Asp.net
- C#
- Oracle
- MS-SQL
- MariaDB
- Mysql
- Postgre
- React
- Vue.js
"""

resume_improver = ResumeImprover(url=url)
resume_improver.create_draft_tailored_resume()


# pdf_generator = ResumePDFGenerator()
# pdf_generator.generate_resume(
#     "resume",
#     utils.read_yaml(filename="data/Website_Toolbox_Sr._Software_Engineer/resume.yaml"),
# )
