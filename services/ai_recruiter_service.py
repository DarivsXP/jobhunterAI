"""
Optional OpenAI-based recruiter enrichment.
"""

from __future__ import annotations

import json
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
    _url = "https://api.openai.com/v1/responses"
    _prompt_path = Path("prompts/recruiter.txt")

    def is_enabled(self) -> bool:
        return bool(settings.openai_api_key)

    def evaluate(self, job: Job) -> AIRecruiterAnalysis | None:
        if not self.is_enabled():
            return None

        prompt = self._build_prompt(job)
        payload = {
            "model": settings.openai_model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        }
                    ],
                }
            ],
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
            return self._parse_response(response.json(), job)

        except Exception:
            logger.exception(
                "OpenAI recruiter enrichment failed for %s (%s)",
                job.title,
                job.company,
            )
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
        output_text = payload.get("output_text", "").strip()

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
