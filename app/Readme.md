# ResumeGPT Endpoint

we have developed a FastAPI-based application that processes and tailors resumes based on job descriptions or URLs. It converts uploaded PDF resumes to YAML format using OpenAI's API, enhances the resume content to align with job requirements, and generates a tailored PDF resume using customizable templates.

## Features
- **PDF to YAML Conversion**: Converts uploaded PDF resumes to YAML format using OpenAI's API.
- **Resume Tailoring**: Enhances resumes based on provided job descriptions or job URLs.
- **Customizable Templates**: Generates PDF resumes using different templates (e.g., "classic").
- **Background File Cleanup**: Automatically removes temporary files to manage disk space.
- **Error Handling**: Robust validation and error handling for inputs and file processing.
- **Performance Logging**: Tracks and logs processing times for debugging and optimization.

# API Endpoint Documentation

## POST `/process-resume/`

This endpoint processes a resume and generates a tailored PDF based on provided job details. It supports uploading a PDF resume, converting it to YAML using OpenAI’s API, tailoring it to a job description or URL, and generating a PDF using a specified template.

### Request Parameters

- **resume_file** (optional, file)
  - Description: A PDF resume to process.
  - Default: If not provided, uses the default resume from `config.DEFAULT_RESUME_PATH` (`data/sample_resume.yaml`).
  - Constraints: Must be a valid PDF file if provided.

- **job_url** (optional, string)
  - Description: URL of the job posting to tailor the resume.
  - Default: None.
  - Constraints: Either `job_url` or `job_description` must be provided.

- **job_description** (optional, string)
  - Description: Text of the job description to tailor the resume.
  - Default: None.
  - Constraints: Either `job_url` or `job_description` must be provided.

- **template_name** (string)
  - Description: Name of the resume template to use for PDF generation.
  - Default: `"classic"`.
  - Example: `"classic"`, `"modern"`.

- **manual_review** (boolean)
  - Description: If `true`, enables manual review mode [ For API testing Always Turn this false].
  - Default: `false`.

- **api_key** (optional, string)
  - Description: OpenAI API key for PDF-to-YAML conversion, This must be provieded this is not optional. [ Will change this in next updaate]
  - Default: None.
  - Constraints: Required if `resume_file` is provided and `OPENAI_API_KEY` is not set in the environment.

### Request Constraints

- At least one of `job_url` or `job_description` must be provided.
- If `resume_file` is provided, it must be a valid PDF file.
- If `api_key` is not provided and `OPENAI_API_KEY` is not set in the environment, an error will be raised when processing an uploaded resume.

### Response

- **Success**:
  - Status Code: 200
  - Content: A downloadable PDF file named `tailored_resume_{template_name}.pdf`.
  - Media Type: `application/pdf`

