import os
import time
import subprocess
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup
import uuid
import requests
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from models.resume import (
    ResumeImproverOutput,
    ResumeSkillsMatcherOutput,
    ResumeSummarizerOutput,
    ResumeSectionHighlighterOutput,
)
import utils
import config
from .langchain_helpers import *
from prompts import Prompts
from models.job_post import JobPost
from pdf_generation import ResumePDFGenerator
import concurrent.futures
from fp.fp import FreeProxy
import time
from config import config
from .background_runner import BackgroundRunner


class ResumeImprover:

    def __init__(
        self,
        url=None,
        job_description=None,
        resume_location=None,
        llm_kwargs: dict = None,
    ):
        """Initialize ResumeImprover with the job post URL and optional resume location.

        Args:
            url (str): The URL of the job post.
            resume_location (str, optional): The file path to the resume. Defaults to None.
            llm_kwargs (dict, optional): Additional keyword arguments for the language model. Defaults to None.
        """
        super().__init__()
        self.job_post_html_data = None
        self.job_post_raw = None
        self.resume = None
        self.resume_yaml = None
        self.job_post = None
        self.parsed_job = None
        self.llm_kwargs = llm_kwargs or {}
        self.editing = False
        self.clean_url = None
        self.job_data_location = None
        self.yaml_loc = None
        self.url = url
        self.job_description = job_description
        
        # Cache for API responses to avoid duplicate calls
        self._api_cache = {}
        
        self.download_and_parse_job_post(job_description=self.job_description)
        self.resume_location = resume_location or config.DEFAULT_RESUME_PATH
        self._update_resume_fields()

    def _get_cache_key(self, prompt_type: str, section_data: str = None) -> str:
        """Generate a cache key for API responses based on content hash."""
        import hashlib
        content = f"{prompt_type}_{self.job_post_raw}_{section_data or ''}"
        return hashlib.md5(content.encode()).hexdigest()

    def _update_resume_fields(self):
        """Update the resume fields based on the current resume location."""
        utils.check_resume_format(self.resume_location)
        self.resume = utils.read_yaml(filename=self.resume_location)
        self.degrees = self._get_degrees(self.resume)
        self.basic_info = utils.get_dict_field(field="basic", data_dict=self.resume)
        self.education = utils.get_dict_field(field="education", data_dict=self.resume)
        self.experiences = utils.get_dict_field(
            field="experiences", data_dict=self.resume
        )
        self.projects = utils.get_dict_field(field="projects", data_dict=self.resume)
        self.skills = utils.get_dict_field(field="skills", data_dict=self.resume)
        self.objective = utils.get_dict_field(field="objective", data_dict=self.resume)

    def update_resume(self, new_resume_location):
        """Update the resume location and refresh the dependent fields.

        Args:
            new_resume_location (str): The new file path to the resume.
        """
        self.resume_location = new_resume_location
        self._update_resume_fields()
        # Clear cache when resume changes
        self._api_cache.clear()

    def _extract_html_data(self):
        """Extract text content from HTML, removing all HTML tags.

        Raises:
            Exception: If HTML data extraction fails.
        """
        try:
            soup = BeautifulSoup(self.job_post_html_data, "html.parser")
            self.job_post_raw = soup.get_text(separator=" ", strip=True)
        except Exception as e:
            config.logger.error(f"Failed to extract HTML data: {e}")
            raise

    def _download_url(self, url=None):
        """Download the content of the URL and return it as a string.

        Args:
            url (str, optional): The URL to download. Defaults to None.

        Returns:
            bool: True if download was successful, False otherwise.
        """
        if url:
            self.url = url

        max_retries = config.MAX_RETRIES
        backoff_factor = config.BACKOFF_FACTOR
        use_proxy = False

        for attempt in range(max_retries):
            try:
                proxies = None
                if use_proxy:
                    proxy = FreeProxy(rand=True).get()
                    proxies = {"http": proxy, "https": proxy}

                response = requests.get(
                    self.url, headers=config.REQUESTS_HEADERS, proxies=proxies
                )
                response.raise_for_status()
                self.job_post_html_data = response.text
                return True

            except requests.RequestException as e:
                if response.status_code == 429:
                    config.logger.warning(
                        f"Rate limit exceeded. Retrying in {backoff_factor * 2 ** attempt} seconds..."
                    )
                    time.sleep(backoff_factor * 2**attempt)
                    use_proxy = True
                else:
                    config.logger.error(f"Failed to download URL {self.url}: {e}")
                    return False

        config.logger.error(f"Exceeded maximum retries for URL {self.url}")
        return False

    def download_and_parse_job_post(self, url=None, job_description=None):
        """Download and parse the job post from the provided URL.

        Args:
            url (str, optional): The URL of the job post. Defaults to None.
        """
        if self.url:
            self._download_url()
            self._extract_html_data()
        elif self.job_description:
            self.job_post_raw = job_description
        else:
            raise ValueError("Either url or job_description must be provided")

        self.job_post = JobPost(self.job_post_raw)
        self.parsed_job = self.job_post.parse_job_post(verbose=False)
        try:
            filename = self.parsed_job["company"] + "_" + self.parsed_job["job_title"]
            filename = filename.replace(" ", "_")
        except KeyError:
            if "://" in self.url:
                filename = self.url.split("://")[1]
            else:
                filename = self.url
            url_paths = filename.split("/")
            filename = url_paths[0]
            if len(url_paths) > 1:
                filename = filename + "." + url_paths[-1]
        self.clean_url = filename
        filepath = os.path.join(config.DATA_PATH, self.clean_url)
        self.job_data_location = filepath
        os.makedirs(self.job_data_location, exist_ok=True)
        utils.write_yaml(
            self.parsed_job, filename=os.path.join(self.job_data_location, "job.yaml")
        )

    def parse_raw_job_post(self, raw_html):
        """Download and parse the job post from the provided URL.

        Args:
            url (str, optional): The URL of the job post. Defaults to None.
        """
        self.job_post_html_data = raw_html
        self._extract_html_data()
        self.job_post = JobPost(self.job_post_raw)
        self.parsed_job = self.job_post.parse_job_post(verbose=False)
        try:
            filename = self.parsed_job["company"] + "_" + self.parsed_job["job_title"]
            filename = filename.replace(" ", "_")
        except KeyError:
            if "://" in self.url:
                filename = self.url.split("://")[1]
            else:
                filename = self.url
            url_paths = filename.split("/")
            filename = url_paths[0]
            if len(url_paths) > 1:
                filename = filename + "." + url_paths[-1]
        self.clean_url = filename
        filepath = os.path.join(config.DATA_PATH, self.clean_url)
        self.job_data_location = filepath
        os.makedirs(self.job_data_location, exist_ok=True)
        utils.write_yaml(
            self.parsed_job, filename=os.path.join(self.job_data_location, "job.yaml")
        )

    def create_draft_tailored_resume_batch(
        self, auto_open=True, manual_review=True, skip_pdf_create=False
    ):
        """Run a full review of the resume against the job post using batch processing.

        Args:
            auto_open (bool, optional): Whether to automatically open the generated resume. Defaults to True.
            manual_review (bool, optional): Whether to wait for manual review. Defaults to True.
        """
        config.logger.info("Starting batch processing for resume optimization...")
        
        # Process all sections in a single batch API call
        batch_results = self._process_all_sections_batch()
        
        # Extract results from batch response
        self.skills = batch_results.get('skills', self.skills)
        self.objective = batch_results.get('objective', self.objective)
        self.experiences = batch_results.get('experiences', self.experiences)
        self.projects = batch_results.get('projects', self.projects)
        
        config.logger.info("Done updating...")
        self.yaml_loc = os.path.join(self.job_data_location, "resume.yaml")
        resume_dict = dict(
            editing=True,
            basic=self.basic_info,
            objective=self.objective,
            education=self.education,
            experiences=self.experiences,
            projects=self.projects,
            skills=self.skills,
        )
        utils.write_yaml(resume_dict, filename=self.yaml_loc)
        self.resume_yaml = utils.read_yaml(filename=self.yaml_loc)
        
        if auto_open:
            subprocess.run(f"start {self.yaml_loc}", shell=True)
        while manual_review and utils.read_yaml(filename=self.yaml_loc)["editing"]:
            time.sleep(5)
        config.logger.info("Generating PDF")
        if not skip_pdf_create:
            self.create_pdf(auto_open=auto_open)

    def _process_all_sections_batch(self):
        """Process all resume sections in a single batch API call to minimize API usage."""
        
        # Create a combined prompt that handles all sections at once
        combined_prompt = self._create_combined_prompt()
        
        # Use a single LLM call for all processing
        llm = create_llm(**self.llm_kwargs)
        
        # Create structured output for all sections
        from pydantic import BaseModel, Field
        from typing import List
        
        class SkillCategory(BaseModel):
            category: str = Field(description="The skill category name")
            skills: List[str] = Field(description="List of skills in this category")
        
        class ExperienceHighlight(BaseModel):
            company: str = Field(description="Company name")
            title: str = Field(description="Job title")
            highlights: List[str] = Field(description="Optimized bullet points")
        
        class ProjectHighlight(BaseModel):
            name: str = Field(description="Project name")
            highlights: List[str] = Field(description="Optimized bullet points")
        
        class BatchResumeOutput(BaseModel):
            technical_skills: List[str] = Field(description="Technical skills that match the job")
            non_technical_skills: List[str] = Field(description="Non-technical skills that match the job")
            objective: str = Field(description="Tailored objective statement")
            experience_highlights: List[List[str]] = Field(description="Rewritten highlights for each experience")
            project_highlights: List[List[str]] = Field(description="Rewritten highlights for each project")
        
        # Single API call for all sections
        runnable = combined_prompt | llm.with_structured_output(schema=BatchResumeOutput)
        
        # Get all inputs needed
        chain_inputs = {
            'job_description': self.job_post_raw,
            'parsed_job': str(self.parsed_job),
            'current_skills': chain_formatter('skills', self.skills),
            'current_experiences': chain_formatter('experience', self.experiences),
            'current_projects': chain_formatter('projects', self.projects),
            'basic_info': str(self.basic_info),
            'education': chain_formatter('education', self.education),
            'degrees': ', '.join(self.degrees) if self.degrees else '',
            'num_experiences': len(self.experiences),
            'num_projects': len(self.projects)
        }
        
        try:
            result = runnable.invoke(chain_inputs)
            
            # Convert the result back to the expected format
            processed_result = {
                'skills': [
                    {'category': 'Technical', 'skills': result.technical_skills},
                    {'category': 'Non-technical', 'skills': result.non_technical_skills}
                ],
                'objective': result.objective,
                'experiences': [],
                'projects': []
            }
            
            # Map experience highlights back to original structure
            for i, exp in enumerate(self.experiences):
                exp_copy = dict(exp)
                if i < len(result.experience_highlights):
                    exp_copy['highlights'] = result.experience_highlights[i]
                processed_result['experiences'].append(exp_copy)
            
            # Map project highlights back to original structure  
            for i, proj in enumerate(self.projects):
                proj_copy = dict(proj)
                if i < len(result.project_highlights):
                    proj_copy['highlights'] = result.project_highlights[i]
                processed_result['projects'].append(proj_copy)
            
            return processed_result
            
        except Exception as e:
            config.logger.error(f"Batch processing failed: {e}")
            # Fallback to individual processing with caching
            return self._process_sections_with_cache()

    def _create_combined_prompt(self):
        """Create a combined prompt template for batch processing."""
        
        combined_template = """
        You are a professional resume optimizer. Given a job description and current resume sections, 
        optimize ALL sections simultaneously to match the job requirements.
        
        Job Description:
        {job_description}
        
        Parsed Job Requirements:
        {parsed_job}
        
        Current Resume Sections:
        
        Basic Info: {basic_info}
        Education: {education}
        Degrees: {degrees}
        
        Current Skills:
        {current_skills}
        
        Current Experiences ({num_experiences} experiences):
        {current_experiences}
        
        Current Projects ({num_projects} projects):
        {current_projects}
        
        Please provide:
        1. technical_skills: Array of technical skills that match the job (extract from job description and current skills)
        2. non_technical_skills: Array of soft skills that match the job (extract from job description and current skills)
        3. objective: A tailored objective statement for this specific job
        4. experience_highlights: Array of arrays - for each of the {num_experiences} experiences, provide optimized bullet points
        5. project_highlights: Array of arrays - for each of the {num_projects} projects, provide optimized bullet points
        
        Focus on keywords from the job description and quantifiable achievements.
        Maintain truthfulness while optimizing for relevance.
        Ensure the arrays match the exact count of experiences and projects provided.
        """
        
        return ChatPromptTemplate.from_template(combined_template)

    def _process_sections_with_cache(self):
        """Fallback method using individual API calls with caching."""
        results = {}
        
        # Process with caching to avoid duplicate calls
        cache_key_skills = self._get_cache_key("skills")
        if cache_key_skills not in self._api_cache:
            self._api_cache[cache_key_skills] = self.extract_matched_skills(verbose=False)
        results['skills'] = self._api_cache[cache_key_skills]
        
        cache_key_objective = self._get_cache_key("objective")
        if cache_key_objective not in self._api_cache:
            self._api_cache[cache_key_objective] = self.write_objective(verbose=False)
        results['objective'] = self._api_cache[cache_key_objective]
        
        # Process experiences and projects with parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            exp_future = executor.submit(self.rewrite_unedited_experiences_cached, verbose=False)
            proj_future = executor.submit(self.rewrite_unedited_projects_cached, verbose=False)
            
            results['experiences'] = exp_future.result()
            results['projects'] = proj_future.result()
        
        return results

    def create_draft_tailored_resume(
        self, auto_open=True, manual_review=True, skip_pdf_create=False
    ):
        """Run a full review of the resume against the job post.
        
        This method now uses the optimized batch processing approach.
        """
        return self.create_draft_tailored_resume_batch(auto_open, manual_review, skip_pdf_create)

    def _create_tailored_resume_in_background(
        self, auto_open=True, manual_review=True, background_runner=None
    ):
        """Run a full review of the resume against the job post using optimized processing."""
        if background_runner is not None:
            logger = background_runner.logger
        else:
            logger = config.logger
            
        logger.info("Starting optimized background processing...")
        
        # Use batch processing for background jobs too
        batch_results = self._process_all_sections_batch()
        
        self.skills = batch_results.get('skills', self.skills)
        self.objective = batch_results.get('objective', self.objective)
        self.experiences = batch_results.get('experiences', self.experiences)
        self.projects = batch_results.get('projects', self.projects)
        
        logger.info("Done updating...")
        self.yaml_loc = os.path.join(self.job_data_location, "resume.yaml")
        resume_dict = dict(
            editing=True,
            basic=self.basic_info,
            objective=self.objective,
            education=self.education,
            experiences=self.experiences,
            projects=self.projects,
            skills=self.skills,
        )
        utils.write_yaml(resume_dict, filename=self.yaml_loc)
        self.resume_yaml = utils.read_yaml(filename=self.yaml_loc)

    @staticmethod
    def create_draft_tailored_resumes_in_background(background_configs: List[dict]):
        """Run 'create_draft_tailored_resume' for multiple configurations in the background.

        Args:
            background_configs (List[dict]): List of configurations for creating draft tailored resumes.
        """
        output = {}
        output["ResumeImprovers"] = []
        output["background_runner"] = BackgroundRunner()

        def run_config(background_config, resume_improver):
            try:
                resume_improver.download_and_parse_job_post()
                resume_improver._create_tailored_resume_in_background(
                    auto_open=background_config.get("auto_open", True),
                    manual_review=background_config.get("manual_review", True),
                    background_runner=output["background_runner"]
                )
            except Exception as e:
                output["background_runner"].logger.error(
                    f"An error occurred with config {background_config}: {e}"
                )

        for background_config in background_configs:
            output["ResumeImprovers"].append(
                ResumeImprover(
                    url=background_config["url"],
                    resume_location=background_config.get("resume_location"),
                )
            )
            output["background_runner"].run_in_background(
                run_config, background_config, output["ResumeImprovers"][-1]
            )
        return output

    def _get_formatted_chain_inputs(self, chain, section=None):
        output_dict = {}
        raw_self_data = self.__dict__
        if section is not None:
            raw_self_data = raw_self_data.copy()
            raw_self_data["section"] = section
        for key in chain.get_input_schema().schema()["required"]:
            output_dict[key] = chain_formatter(
                key, raw_self_data.get(key) or self.parsed_job.get(key)
            )
        return output_dict

    def _chain_updater(
        self, prompt_msgs, pydantic_object, **chain_kwargs
    ) -> RunnableSequence:
        """Create a chain based on the prompt messages.

        Returns:
            RunnableSequence: The chain for highlighting resume sections, matching skills, or improving resume content.
        """
        prompt = ChatPromptTemplate(messages=prompt_msgs)
        llm = create_llm(**self.llm_kwargs)
        runnable = prompt | llm.with_structured_output(schema=pydantic_object)
        return runnable

    def _get_degrees(self, resume: dict):
        """Extract degrees from the resume.

        Args:
            resume (dict): The resume data.

        Returns:
            list: A list of degree names.
        """
        result = []
        for degrees in utils.generator_key_in_nested_dict("degrees", resume):
            for degree in degrees:
                if isinstance(degree["names"], list):
                    result.extend(degree["names"])
                elif isinstance(degree["names"], str):
                    result.append(degree["names"])
        return result

    def _combine_skills_in_category(self, l1: list[str], l2: list[str]):
        """Combine two lists of skills without duplicating lowercase entries."""
        l1_lower = {i.lower() for i in l1}
        for i in l2:
            if i.lower() not in l1_lower:
                l1.append(i)

    def _combine_skill_lists(self, l1: list[dict], l2: list[dict]):
        """Combine two lists of skill categories without duplicating lowercase entries."""
        l1_categories_lowercase = {s["category"].lower(): i for i, s in enumerate(l1)}
        for s in l2:
            if s["category"].lower() in l1_categories_lowercase:
                self._combine_skills_in_category(
                    l1[l1_categories_lowercase[s["category"].lower()]]["skills"],
                    s["skills"],
                )
            else:
                l1.append(s)

    def rewrite_section_cached(self, section: list | str, **chain_kwargs) -> dict:
        """Rewrite a section of the resume with caching."""
        section_str = str(section)
        cache_key = self._get_cache_key("section_highlight", section_str)
        
        if cache_key in self._api_cache:
            return self._api_cache[cache_key]
        
        result = self.rewrite_section(section, **chain_kwargs)
        self._api_cache[cache_key] = result
        return result

    def rewrite_section(self, section: list | str, **chain_kwargs) -> dict:
        """Rewrite a section of the resume."""
        chain = self._chain_updater(
            Prompts.lookup["SECTION_HIGHLIGHTER"],
            ResumeSectionHighlighterOutput,
            **chain_kwargs,
        )
        chain_inputs = self._get_formatted_chain_inputs(chain=chain, section=section)
        section_revised = chain.invoke(chain_inputs).dict()
        section_revised = sorted(
            section_revised["final_answer"], key=lambda d: d["relevance"] * -1
        )
        return [s["highlight"] for s in section_revised]

    def rewrite_unedited_experiences_cached(self, **chain_kwargs) -> dict:
        """Rewrite unedited experiences with caching."""
        cache_key = self._get_cache_key("experiences", str(self.experiences))
        
        if cache_key in self._api_cache:
            return self._api_cache[cache_key]
        
        result = self.rewrite_unedited_experiences(**chain_kwargs)
        self._api_cache[cache_key] = result
        return result

    def rewrite_unedited_experiences(self, **chain_kwargs) -> dict:
        """Rewrite unedited experiences in the resume."""
        result = []
        for exp in self.experiences:
            exp = dict(exp)
            exp["highlights"] = self.rewrite_section_cached(section=exp, **chain_kwargs)
            result.append(exp)
        return result

    def rewrite_unedited_projects_cached(self, **chain_kwargs) -> dict:
        """Rewrite unedited projects with caching."""
        cache_key = self._get_cache_key("projects", str(self.projects))
        
        if cache_key in self._api_cache:
            return self._api_cache[cache_key]
        
        result = self.rewrite_unedited_projects(**chain_kwargs)
        self._api_cache[cache_key] = result
        return result

    def rewrite_unedited_projects(self, **chain_kwargs) -> dict:
        """Rewrite unedited projects in the resume."""
        result = []
        for exp in self.projects:
            exp = dict(exp)
            exp["highlights"] = self.rewrite_section_cached(section=exp, **chain_kwargs)
            result.append(exp)
        return result

    def extract_matched_skills(self, **chain_kwargs) -> dict:
        """Extract matched skills from the resume and job post."""
        chain = self._chain_updater(
            Prompts.lookup["SKILLS_MATCHER"], ResumeSkillsMatcherOutput, **chain_kwargs
        )
        chain_inputs = self._get_formatted_chain_inputs(chain=chain)
        extracted_skills = chain.invoke(chain_inputs).dict()
        if not extracted_skills or "final_answer" not in extracted_skills:
            return None
        extracted_skills = extracted_skills["final_answer"]
        result = []
        if "technical_skills" in extracted_skills:
            result.append(
                dict(category="Technical", skills=extracted_skills["technical_skills"])
            )
        if "non_technical_skills" in extracted_skills:
            result.append(
                dict(
                    category="Non-technical",
                    skills=extracted_skills["non_technical_skills"],
                )
            )
        self._combine_skill_lists(result, self.skills)
        return result

    def write_objective(self, **chain_kwargs) -> dict:
        """Write a objective for the resume."""
        chain = self._chain_updater(
            Prompts.lookup["OBJECTIVE_WRITER"], ResumeSummarizerOutput, **chain_kwargs
        )

        chain_inputs = self._get_formatted_chain_inputs(chain=chain)
        objective = chain.invoke(chain_inputs).dict()
        if not objective or "final_answer" not in objective:
            return None
        return objective["final_answer"]

    def suggest_improvements(self, **chain_kwargs) -> dict:
        """Suggest improvements for the resume."""
        chain = self._chain_updater(
            Prompts.lookup["IMPROVER"], ResumeImproverOutput, **chain_kwargs
        )
        chain_inputs = self._get_formatted_chain_inputs(chain=chain)
        improvements = chain.invoke(chain_inputs).dict()
        if not improvements or "final_answer" not in improvements:
            return None
        return improvements["final_answer"]

    def finalize(self) -> dict:
        """Finalize the resume data."""
        return dict(
            basic=self.basic_info,
            objective=self.objective,
            education=self.education,
            experiences=self.experiences,
            projects=self.projects,
            skills=self.skills,
        )

    def create_pdf(self, auto_open=True):
        """Create a PDF of the resume."""
        pdf_generator = ResumePDFGenerator()
        pdf_location = pdf_generator.generate_resume(
            job_data_location=self.job_data_location,
            data=utils.read_yaml(filename=self.yaml_loc),
        )
        if auto_open:
            subprocess.run(config.OPEN_FILE_COMMAND.split(" ") + [pdf_location])
        return pdf_location