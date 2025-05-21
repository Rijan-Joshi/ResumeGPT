from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
import os
import tempfile
import warnings
import utils
from services.resume_improver import ResumeImprover
from pdf_generation.resume_pdf_generator import ResumePDFGenerator
from config import config
from config.config import logger
import time  # Added for timing measurements

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
    try:
        
        start_time_pdf = time.time()
        
        if "OPENAI_API_KEY" not in os.environ:
            logger.info(
                "OPENAI_API_KEY not found in environment. Api key will be taken from the FastAPI endpoint"
            )
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Validate job input
        if not job_url and not job_description:
            raise HTTPException(status_code=400, detail="Either job_url or job_description must be provided")
        
        # Determine which resume to use
        resume_path = config.DEFAULT_RESUME_PATH  # currently this is pointing to data/sample_resume.yaml
        temp_pdf_path = None
        
        # Process uploaded resume if provided
        if resume_file:
            # Get API key from form or environment
            if not api_key:
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise HTTPException(
                        status_code=400, 
                        detail="OpenAI API key is required to process resume. Either provide it in the form or set OPENAI_API_KEY environment variable."
                    )
            
            # Check if the uploaded file is a PDF
            if not resume_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")
            
            # Create a temporary file to store the uploaded PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                # Read the uploaded file content
                content = await resume_file.read()
                # Write content to temporary file
                temp_pdf.write(content)
                temp_pdf_path = temp_pdf.name
            
            try:
                yaml_filename = f"sample_resume.yaml"  # using the name same as the default path name, we can change this later
                yaml_path = os.path.join(data_dir, yaml_filename)
                
                # Initialize the converter with the provided API key
                converter = OpenAIPDFToYAMLConverter(api_key=api_key)
                
                # Convert the PDF to YAML and measure time
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
                
                # Update resume path to use the converted YAML
                resume_path = yaml_path
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing uploaded resume: {str(e)}")
        
        # Initialize ResumeImprover with the appropriate resume location
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
        yaml_path = resume_improver.yaml_loc
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Resume YAML not found at {yaml_path}")

        resume_data = utils.read_yaml(filename=yaml_path)

       
        
        pdf_location = pdf_generator.generate_resume(output_dir, resume_data)
      
        
        # Add cleanup of temporary files to background tasks
        if temp_pdf_path:
            background_tasks.add_task(os.unlink, temp_pdf_path)

        
        end_time_pdf = time.time()
        Total_Time = end_time_pdf - start_time_pdf
        logger.info(f"Total Time {Total_Time:.2f} seconds")
        # Return the PDF as a downloadable file
        filename = f"tailored_resume_{template_name}.pdf"
        return FileResponse(
            path=pdf_location,
            filename=filename,
            media_type="application/pdf"
        )

    except FileNotFoundError as e:
        # Cleanup temp files in case of error
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)
        raise HTTPException(status_code=404, detail=str(e))
    
    except HTTPException:
        # Cleanup temp files in case of error
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)
        raise
    
    except Exception as e:
        # Cleanup temp files in case of error
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")