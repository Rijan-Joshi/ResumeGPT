import streamlit as st
import requests
import re
from urllib.parse import unquote

# FastAPI endpoint URL
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

# Define function to extract processing times from logs
def extract_processing_times(logs):
    times = {}
    yaml_match = re.search(r"PDF to YAML conversion took ([\d.]+) seconds", logs)
    total_match = re.search(r"Total Time ([\d.]+) seconds", logs)
    if yaml_match:
        times["yaml_conversion"] = float(yaml_match.group(1))
    if total_match:
        times["total"] = float(total_match.group(1))
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

    # FIXED: Removed invalid 'key' argument
    submit_button = st.form_submit_button("Generate Resume")

# Handle form submission
if submit_button and (job_url.strip() or job_description.strip()):
    try:
        # Prepare data and file
        data = {
            "job_url": job_url or None,
            "job_description": job_description or None,
            "template_name": template_name,
            "manual_review": manual_review,
            "api_key": api_key or None
        }

        files = {}
        if resume_file:
            files["resume_file"] = (resume_file.name, resume_file.getvalue(), "application/pdf")

        with st.spinner("Processing your resume..."):
            response = requests.post(API_URL, data=data, files=files or None, timeout=300)

        if response.status_code == 200:
            # Extract filename from headers
            content_disp = response.headers.get("Content-Disposition", "")
            filename = "tailored_resume.pdf"
            match = re.search(r'filename="([^"]+)"', content_disp)
            if match:
                filename = unquote(match.group(1))

            # Store file for download
            st.session_state.download_file = {
                "content": response.content,
                "filename": filename
            }

            # Get logs if available
            logs = response.text if "text/plain" in response.headers.get("Content-Type", "") else ""
            st.session_state.processing_times = extract_processing_times(logs)

            st.session_state.success_message = "Resume generated successfully! Download the file below."
            st.session_state.error_message = None
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.session_state.error_message = f"Error: {error_detail}"
            st.session_state.success_message = None
            st.session_state.download_file = None

    except requests.exceptions.RequestException as e:
        st.session_state.error_message = f"Failed to connect to the server: {e}"
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
