"""
Optional OpenAI-based recruiter enrichment.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from candidate.profile import MY_PROFILE
from config.settings import settings
from core.logger import get_logger
from core.models import Job

logger = get_logger(__name__)


@dataclass(slots=True)
class AIRecruiterAnalysis:
    interview_probability: int
    matched_skills: list[str]
    missing_skills: list[str]
    recommendation: str
    reasoning: str


class AIRecruiterService:
    _url = settings.openai_base_url
    _prompt_path = Path("prompts/recruiter.txt")

    def is_enabled(self) -> bool:
        return bool(settings.openai_api_key)

    def evaluate(self, job: Job) -> AIRecruiterAnalysis | None:
        if not self.is_enabled():
            return None

        prompt = self._build_prompt(job)
        payload = {
            "model": settings.openai_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "response_format": {"type": "json_object"},
        }

        # Retry up to 3 times with exponential back-off on rate-limit errors
        retry_delays = [2, 8, 20]
        for attempt, delay in enumerate(retry_delays, start=1):
            try:
                response = requests.post(
                    self._url,
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=60,
                )

                if response.status_code == 429:
                    if attempt < len(retry_delays):
                        logger.warning(
                            "OpenAI rate limited (429) for %s — retrying in %ds (attempt %d/%d)",
                            job.title, delay, attempt, len(retry_delays),
                        )
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(
                            "OpenAI rate limited (429) for %s — giving up after %d attempts",
                            job.title, len(retry_delays),
                        )
                        return None

                response.raise_for_status()
                return self._parse_response(response.json(), job)

            except Exception:
                logger.exception(
                    "OpenAI recruiter enrichment failed for %s (%s)",
                    job.title,
                    job.company,
                )
                return None

        return None

    def generate_application_materials(self, job_dict: dict[str, Any]) -> dict[str, Any] | None:
        if not self.is_enabled():
            return None

        skills = ", ".join(MY_PROFILE.preferred_skills)
        prompt = (
            "You are an expert career coach and technical recruiter. "
            "I need a highly tailored cover letter and 3-5 customized resume bullet points for this job.\n\n"
            f"Candidate: {MY_PROFILE.name}\n"
            f"Level: {MY_PROFILE.experience_level}\n"
            f"Summary: {MY_PROFILE.summary}\n"
            f"Skills: {skills}\n\n"
            f"Job Title: {job_dict.get('title')}\n"
            f"Company: {job_dict.get('company')}\n"
            f"Description: {job_dict.get('description')}\n\n"
            "Return JSON only with keys: 'cover_letter' (string) and 'resume_bullets' (list of strings)."
        )

        payload = {
            "model": settings.openai_model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }

        try:
            response = requests.post(
                self._url,
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            
            choices = response.json().get("choices", [])
            if not choices:
                return None
                
            output_text = choices[0].get("message", {}).get("content", "").strip()
            data = json.loads(output_text)
            
            return {
                "cover_letter": str(data.get("cover_letter", "")).strip(),
                "resume_bullets": [str(b).strip() for b in data.get("resume_bullets", []) if str(b).strip()]
            }
        except Exception:
            logger.exception("Failed to generate application materials for %s", job_dict.get('title'))
            return None

    def _build_prompt(self, job: Job) -> str:
        template = self._load_prompt_template()
        skills = ", ".join(MY_PROFILE.preferred_skills)
        roles = ", ".join(MY_PROFILE.preferred_roles)
        countries = ", ".join(MY_PROFILE.preferred_countries)

        return template.format(
            candidate_name=MY_PROFILE.name,
            candidate_level=MY_PROFILE.experience_level,
            candidate_summary=MY_PROFILE.summary,
            preferred_roles=roles,
            preferred_skills=skills,
            preferred_countries=countries,
            job_title=job.title,
            job_company=job.company,
            job_country=job.country,
            job_posted_at=job.posted_at,
            job_source=job.source,
            job_salary=job.salary,
            job_url=job.url,
            job_description=job.description,
        )

    def _load_prompt_template(self) -> str:
        if self._prompt_path.exists():
            content = self._prompt_path.read_text(encoding="utf-8").strip()
            if content:
                return content

        return (
            "You are an experienced technical recruiter.\n"
            "Evaluate the candidate-job fit and return JSON only with keys: "
            "interview_probability, matched_skills, missing_skills, "
            "recommendation, reasoning.\n\n"
            "Candidate: {candidate_name}\n"
            "Level: {candidate_level}\n"
            "Summary: {candidate_summary}\n"
            "Preferred roles: {preferred_roles}\n"
            "Preferred skills: {preferred_skills}\n"
            "Preferred countries: {preferred_countries}\n\n"
            "Job title: {job_title}\n"
            "Company: {job_company}\n"
            "Country: {job_country}\n"
            "Posted at: {job_posted_at}\n"
            "Source: {job_source}\n"
            "Salary: {job_salary}\n"
            "URL: {job_url}\n"
            "Description:\n{job_description}\n"
        )

    def _parse_response(
        self,
        payload: dict[str, Any],
        job: Job,
    ) -> AIRecruiterAnalysis | None:
        choices = payload.get("choices", [])
        if not choices:
            logger.warning(
                "OpenAI recruiter returned no choices for %s (%s)",
                job.title,
                job.company,
            )
            return None

        output_text = choices[0].get("message", {}).get("content", "").strip()

        if not output_text:
            logger.warning(
                "OpenAI recruiter returned no output text for %s (%s)",
                job.title,
                job.company,
            )
            return None

        data = json.loads(output_text)

        return AIRecruiterAnalysis(
            interview_probability=int(
                data.get("interview_probability", job.interview_probability)
            ),
            matched_skills=[
                str(skill).strip()
                for skill in data.get("matched_skills", [])
                if str(skill).strip()
            ],
            missing_skills=[
                str(skill).strip()
                for skill in data.get("missing_skills", [])
                if str(skill).strip()
            ],
            recommendation=str(data.get("recommendation", "")).strip(),
            reasoning=str(data.get("reasoning", "")).strip(),
        )
