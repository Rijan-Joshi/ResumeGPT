from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, Response # Import Response
from typing import Optional
import os
import tempfile
import warnings
import utils
from services.resume_improver import ResumeImprover
from pdf_generation.resume_pdf_generator import ResumePDFGenerator
from config import config
from config.config import logger
import time

# Import our PDF to YAML converter used OpenAI to convert resumes
from pdf2yaml import OpenAIPDFToYAMLConverter

# Setup paths
data_dir = os.path.join("data")
os.makedirs(data_dir, exist_ok=True)

# Suppress warnings
warnings.filterwarnings("ignore", message="Received a Pydantic BaseModel V1 schema")

app = FastAPI()

@app.post("/process-resume/")
async def process_resume(
    background_tasks: BackgroundTasks,
    resume_file: Optional[UploadFile] = File(None),
    job_url: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    template_name: str = Form("classic"),
    manual_review: bool = Form(False),
    api_key: Optional[str] = Form(None)
):
    """
    1. Upload and convert resume to YAML (if provided)
    2. Generate tailored resume based on job details

    - If resume_file is provided, it will be converted to YAML using OpenAI
    - If resume_file is not provided, the default resume from config will be used
    - Either job_url or job_description must be provided
    """
    temp_pdf_path = None # Initialize to None for cleanup
    yaml_conversion_time = 0.0 # Initialize conversion time

    try:
        start_time_total = time.time() # Changed to start_time_total for clarity

        # API Key handling
        if not api_key:
            # If not provided in form, try environment variable
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                # Only raise error if it's actually needed (i.e., for PDF conversion)
                # or if the default resume also relies on it later.
                # For now, it's checked when resume_file is processed.
                pass

        # Validate job input
        if not job_url and not job_description:
            raise HTTPException(status_code=400, detail="Either job_url or job_description must be provided")

        # Determine which resume to use
        resume_path = config.DEFAULT_RESUME_PATH
        if resume_file:
            # API key is definitively required for PDF conversion
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key is required to process an uploaded resume. Please provide it in the form or set OPENAI_API_KEY environment variable."
                )

            # Check if the uploaded file is a PDF
            if not resume_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")

            # Create a temporary file to store the uploaded PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                content = await resume_file.read()
                temp_pdf.write(content)
                temp_pdf_path = temp_pdf.name

            try:
                yaml_filename = f"uploaded_resume.yaml" # Use a distinct name for uploaded resume YAML
                yaml_path = os.path.join(data_dir, yaml_filename)

                converter = OpenAIPDFToYAMLConverter(api_key=api_key)

                start_time_yaml = time.time()
                success = converter.convert_pdf_to_yaml(temp_pdf_path, yaml_path)
                end_time_yaml = time.time()
                yaml_conversion_time = end_time_yaml - start_time_yaml
                logger.info(f"PDF to YAML conversion took {yaml_conversion_time:.2f} seconds")

                if not success:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to convert PDF to YAML. Check server logs for details."
                    )
                resume_path = yaml_path

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing uploaded resume: {str(e)}")

        # Initialize ResumeImprover
        resume_improver = ResumeImprover(
            url=job_url,
            job_description=job_description,
            resume_location=resume_path
        )

        # Generate tailored resume
        resume_improver.create_draft_tailored_resume(
            auto_open=False,
            manual_review=manual_review,
            skip_pdf_create=True
        )

        # Initialize ResumePDFGenerator
        pdf_generator = ResumePDFGenerator(template_name=template_name)

        # Define output directory
        output_dir = os.path.join("resume")
        os.makedirs(output_dir, exist_ok=True)

        # Read the generated resume YAML
        yaml_path_for_pdf = resume_improver.yaml_loc # Use the path where the final tailored YAML is
        if not os.path.exists(yaml_path_for_pdf):
            raise FileNotFoundError(f"Tailored resume YAML not found at {yaml_path_for_pdf}")

        resume_data = utils.read_yaml(filename=yaml_path_for_pdf)

        pdf_location = pdf_generator.generate_resume(output_dir, resume_data)

        end_time_total = time.time()
        total_processing_time = end_time_total - start_time_total
        logger.info(f"Total processing time: {total_processing_time:.2f} seconds")

        # Prepare custom headers for processing times
        headers = {
            "X-Processing-Time-Yaml": str(yaml_conversion_time),
            "X-Processing-Time-Total": str(total_processing_time)
        }

        # Add cleanup of temporary files to background tasks
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            background_tasks.add_task(os.unlink, temp_pdf_path)
        # Also clean up the generated YAML files if they are temporary and not needed after PDF generation
        if resume_path != config.DEFAULT_RESUME_PATH and os.path.exists(resume_path):
             background_tasks.add_task(os.unlink, resume_path) # Clean up generated YAML

        # Return the PDF as a downloadable file with custom headers
        filename = f"tailored_resume_{template_name}.pdf"
        return FileResponse(
            path=pdf_location,
            filename=filename,
            media_type="application/pdf",
            headers=headers # Pass custom headers
        )

    except FileNotFoundError as e:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            background_tasks.add_task(os.unlink, temp_pdf_path)
        raise HTTPException(status_code=404, detail=str(e))

    except HTTPException:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            background_tasks.add_task(os.unlink, temp_pdf_path)
        raise

    except Exception as e:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            background_tasks.add_task(os.unlink, temp_pdf_path)
        # Catch-all for any other unexpected errors
        logger.error(f"An unhandled error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process resume due to an internal server error: {str(e)}")