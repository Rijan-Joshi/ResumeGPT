import argparse
import os
import yaml
import json
import logging
from pypdf import PdfReader
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAIPDFToYAMLConverter:
    def __init__(self, api_key=None):
        """Initialize the converter with an OpenAI API key."""
        # Use provided API key or get from environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Provide it as an argument or set the OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Template for the expected YAML structure
        self.yaml_template = {
            "editing": True,
            "debug": False,
            "basic": {
                "name": "",
                "address": "",
                "email": "",
                "phone": "",
                "websites": []
            },
            "objective": "",
            "education": [],
            "experiences": [],
            "projects": [],
            "skills": []
        }

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None

    def parse_resume_with_openai(self, text):
        """Use OpenAI to parse the resume text into structured data."""
        try:
            # System prompt explaining the task and expected output structure
            system_prompt = """
            You are a resume parsing assistant. Extract structured information from the resume text provided and format it according to the template.
            Follow these instructions carefully:
            
            1. Extract basic information: name, address, email, phone, and any website URLs (especially LinkedIn and GitHub).
            2. Identify the objective or professional summary.
            3. Extract education details including schools and degrees.
            4. Parse work experience including company names, locations, job titles, dates, and bullet points of achievements.
            5. Extract any projects including name, links, dates, and highlights.
            6. Categorize skills into technical and non-technical groups.
            
            Output the information in JSON format that follows this structure exactly:
            {
                "basic": {
                    "name": "Full Name",
                    "address": "City, State",
                    "email": "email@example.com",
                    "phone": "phone number",
                    "websites": ["https://linkedin.com/username", "https://github.com/username"]
                },
                "objective": "Career objective or professional summary text",
                "education": [
                    {
                        "school": "University Name",
                        "degrees": [
                            {
                                "names": ["Degree Name"]
                            }
                        ]
                    }
                ],
                "experiences": [
                    {
                        "company": "Company Name",
                        "skip_name": false,
                        "location": "City, State",
                        "titles": [
                            {
                                "name": "Job Title",
                                "startdate": "YYYY",
                                "enddate": "YYYY or Present"
                            }
                        ],
                        "highlights": ["Achievement 1", "Achievement 2"]
                    }
                ],
                "projects": [
                    {
                        "name": "Project Name",
                        "link": "https://github.com/username/project",
                        "hyperlink": true,
                        "show_link": true,
                        "date": "Month YYYY",
                        "highlights": ["Detail 1", "Detail 2"]
                    }
                ],
                "skills": [
                    {
                        "category": "Technical",
                        "skills": ["Skill 1", "Skill 2", "Skill 3"]
                    },
                    {
                        "category": "Non-technical",
                        "skills": ["Skill 1", "Skill 2"]
                    }
                ]
            }
            
            Make sure the JSON is properly formatted and contains all available information from the resume.
            If any section is missing from the resume, include it in the JSON but leave it empty or with placeholder values.
            """

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",  
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this resume:\n\n{text}"}
                ],
                temperature=0.1,  
                max_tokens=4000
            )

            # Extract and parse the JSON response
            content = response.choices[0].message.content
            
            # Find JSON content in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > 0:
                json_content = content[json_start:json_end]
                parsed_data = json.loads(json_content)
                return parsed_data
            else:
                logger.error("Could not find valid JSON in OpenAI response")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing resume with OpenAI: {e}")
            return None
    
    def create_yaml_structure(self, parsed_data):
        """Create the final YAML structure using the parsed data."""
        try:
            # Start with the template
            resume_data = self.yaml_template.copy()
            
            # Add basic information
            if "basic" in parsed_data:
                resume_data["basic"] = parsed_data["basic"]
            
            # Add objective
            if "objective" in parsed_data:
                resume_data["objective"] = parsed_data["objective"]
            
            # Add education
            if "education" in parsed_data:
                resume_data["education"] = parsed_data["education"]
            
            # Add experiences
            if "experiences" in parsed_data:
                resume_data["experiences"] = parsed_data["experiences"]
            
            # Add projects
            if "projects" in parsed_data:
                resume_data["projects"] = parsed_data["projects"]
            
            # Add skills
            if "skills" in parsed_data:
                resume_data["skills"] = parsed_data["skills"]
            
            return resume_data
            
        except Exception as e:
            logger.error(f"Error creating YAML structure: {e}")
            return self.yaml_template

    def convert_pdf_to_yaml(self, pdf_path, output_path):
        """Convert PDF to YAML format using OpenAI."""
        logger.info(f"Converting PDF: {pdf_path}")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.error("Failed to extract text from PDF")
            return False
        
        # Parse resume with OpenAI
        logger.info("Parsing resume with OpenAI")
        parsed_data = self.parse_resume_with_openai(text)
        if not parsed_data:
            logger.error("Failed to parse resume with OpenAI")
            return False
        
        # Create YAML structure
        logger.info("Creating YAML structure")
        resume_data = self.create_yaml_structure(parsed_data)
        
        # Write to YAML file
        try:
            with open(output_path, 'w') as yaml_file:
                yaml.dump(resume_data, yaml_file, default_flow_style=False, sort_keys=False)
            logger.info(f"YAML file created successfully: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing YAML file: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Convert a resume PDF to YAML format using OpenAI')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--output', '-o', default='resume.yaml', help='Output YAML file path')
    parser.add_argument('--api-key', '-k', help='OpenAI API key (alternatively, set OPENAI_API_KEY environment variable)')
    
    args = parser.parse_args()
    
    try:
        converter = OpenAIPDFToYAMLConverter(api_key=args.api_key)
        success = converter.convert_pdf_to_yaml(args.pdf_path, args.output)
        
        if success:
            print(f"Successfully converted {args.pdf_path} to {args.output}")
        else:
            print("Conversion failed. Check the logs for more information.")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()