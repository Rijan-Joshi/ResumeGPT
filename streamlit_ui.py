import streamlit as st
import requests
import re
from urllib.parse import unquote
import os

if os.getenv("DOCKER_CONTAINER", "false") == "true":
    API_URL = "http://backend:8000/process-resume/"
else:
    API_URL = "http://localhost:8000/process-resume/"


# Page configuration
st.set_page_config(page_title="Resume GPT", page_icon="📄", layout="wide")

# Title and description
st.title("Resume GPT")
st.markdown("""
Upload your resume (PDF) and provide job details to generate a tailored resume.
You can either paste a job description or provide a job URL. Choose a template and
whether to enable manual review. Once processed, download your tailored resume!
""")

# Initialize session state variables
st.session_state.setdefault("success_message", None)
st.session_state.setdefault("error_message", None)
st.session_state.setdefault("processing_times", None)
st.session_state.setdefault("download_file", None)

# Define function to extract processing times from headers
def extract_processing_times_from_headers(headers):
    times = {}
    if "x-processing-time-yaml" in headers:
        try:
            times["yaml_conversion"] = float(headers["x-processing-time-yaml"])
        except ValueError:
            pass # Ignore if not a valid float
    if "x-processing-time-total" in headers:
        try:
            times["total"] = float(headers["x-processing-time-total"])
        except ValueError:
            pass # Ignore if not a valid float
    return times

# Input form
with st.form(key="resume_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Resume Upload")
        resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    with col2:
        st.subheader("Job Details")
        job_url = st.text_input("Job URL (optional)", placeholder="https://example.com/job")
        job_description = st.text_area("Job Description (optional)", height=150)

    st.subheader("Options")
    template_name = st.selectbox("Select Template", ["classic", "modern", "professional"])
    manual_review = st.checkbox("Enable Manual Review")
    api_key = st.text_input("OpenAI API Key (optional)", type="password")

    submit_button = st.form_submit_button("Generate Resume")

# Handle form submission
if submit_button and (job_url.strip() or job_description.strip()):
    if not resume_file and not api_key:
        st.error("OpenAI API Key is required when no resume file is uploaded (to use the default resume with AI processing).")
    else:
        try:
            # Prepare data and file
            data = {
                "job_url": job_url or "", # Send empty string instead of None for Form fields
                "job_description": job_description or "", # Send empty string instead of None for Form fields
                "template_name": template_name,
                "manual_review": str(manual_review).lower(), # Form fields are strings, convert boolean
                "api_key": api_key or "" # Send empty string instead of None for Form fields
            }

            files = {}
            if resume_file:
                files["resume_file"] = (resume_file.name, resume_file.getvalue(), "application/pdf")

            with st.spinner("Processing your resume..."):
                # Use requests.post with 'data' for form fields and 'files' for file uploads
                response = requests.post(API_URL, data=data, files=files, timeout=300)

            if response.status_code == 200:
                # Extract filename from headers
                content_disp = response.headers.get("Content-Disposition", "")
                filename = "tailored_resume.pdf" # Default filename
                match = re.search(r'filename="([^"]+)"', content_disp)
                if match:
                    filename = unquote(match.group(1))

                # Store file for download
                st.session_state.download_file = {
                    "content": response.content, # Access binary content for PDF
                    "filename": filename
                }

                # Get processing times from custom headers
                st.session_state.processing_times = extract_processing_times_from_headers(response.headers)

                st.session_state.success_message = "Resume generated successfully! Download the file below."
                st.session_state.error_message = None
            else:
                # Attempt to parse JSON error detail if available, otherwise use raw text
                try:
                    error_detail = response.json().get("detail", f"Unknown error: {response.text}")
                except requests.exceptions.JSONDecodeError:
                    error_detail = f"Unknown error: {response.text}" # Fallback to raw text if not JSON

                st.session_state.error_message = f"Error: {error_detail}"
                st.session_state.success_message = None
                st.session_state.download_file = None

        except requests.exceptions.RequestException as e:
            st.session_state.error_message = f"Failed to connect to the server or request timed out: {e}"
            st.session_state.success_message = None
            st.session_state.download_file = None
        except Exception as e:
            st.session_state.error_message = f"An unexpected error occurred: {e}"
            st.session_state.success_message = None
            st.session_state.download_file = None

# Show messages and download button
if st.session_state.error_message:
    st.error(st.session_state.error_message)

if st.session_state.success_message:
    st.success(st.session_state.success_message)
    if st.session_state.download_file:
        st.download_button(
            label="Download Tailored Resume",
            data=st.session_state.download_file["content"],
            file_name=st.session_state.download_file["filename"],
            mime="application/pdf"
        )

# Show processing times if available
if st.session_state.processing_times:
    st.subheader("Processing Times")
    times = st.session_state.processing_times
    if "yaml_conversion" in times:
        st.write(f"PDF to YAML Conversion: {times['yaml_conversion']:.2f} seconds")
    if "total" in times:
        st.write(f"Total Processing Time: {times['total']:.2f} seconds")