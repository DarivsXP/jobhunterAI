"""
Candidate Profile

This file represents the candidate and is used across the scoring,
recruiting, and personalization layers.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class CandidateProfile:
    # Basic Information
    name: str
    experience_level: str
    email: str
    portfolio: str
    github: str
    linkedin: str
    summary: str

    # Job Preferences
    remote_only: bool = True
    preferred_roles: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    preferred_countries: list[str] = field(default_factory=list)
    excluded_titles: list[str] = field(default_factory=list)
    target_title_keywords: list[str] = field(default_factory=list)
    prefilter_excluded_keywords: list[str] = field(default_factory=list)
    strong_title_keywords: list[str] = field(default_factory=list)
    discouraged_title_keywords: list[str] = field(default_factory=list)
    junior_title_keywords: list[str] = field(default_factory=list)
    minimum_score: int = 55


MY_PROFILE = CandidateProfile(
    name="V Cyril Darivs Egipto",
    experience_level="Junior Software Developer",
    email="darivsxp@gmail.com",
    portfolio="https://www.cyrilegipto.space/",
    github="https://github.com/DarivsXP",
    linkedin="https://linkedin.com/v-cyril",
    summary=(
        "Junior software developer with internship experience building web "
        "applications and APIs using PHP, Laravel, Python, JavaScript, SQL, "
        "and Git-based workflows."
    ),
    remote_only=True,
    preferred_roles=[
        "Junior Software Engineer",
        "Junior Backend Developer",
        "Backend Developer",
        "Junior Full Stack Developer",
        "Laravel Developer",
        "PHP Developer",
        "Software Developer",
        "Technical Support Engineer",
        "Application Support Engineer",
    ],
    preferred_skills=[
        "PHP",
        "Laravel",
        "Python",
        "JavaScript",
        "HTML",
        "CSS",
        "MySQL",
        "PostgreSQL",
        "SQLite",
        "Git",
        "GitHub",
        "REST API",
    ],
    preferred_countries=[
        "Australia",
        "Canada",
        "United Kingdom",
        "UK",
        "Singapore",
        "New Zealand",
        "Worldwide",
    ],
    excluded_titles=[
        "Senior",
        "Staff",
        "Principal",
        "Lead",
        "Architect",
        "Manager",
        "Director",
        "Head",
        "VP",
    ],
    target_title_keywords=[
        "backend",
        "software engineer",
        "software developer",
        "developer",
        "engineer",
        "full stack",
        "full-stack",
        "php",
        "laravel",
        "python",
        "web developer",
        "application support",
        "technical support engineer",
        "support engineer",
        "intern",
    ],
    prefilter_excluded_keywords=[
        "account manager",
        "accountant",
        "analyst",
        "assistant",
        "bookkeeper",
        "care advocate",
        "client success",
        "content creator",
        "copywriter",
        "creative",
        "customer happiness",
        "customer service",
        "data entry",
        "designer",
        "executive assistant",
        "freelance writer",
        "hr ",
        "human resources",
        "illustrator",
        "marketing",
        "medical",
        "nurse",
        "operations",
        "patient",
        "product manager",
        "project manager",
        "qa lead",
        "recruiter",
        "sales",
        "secretary",
        "social media",
        "speculative application",
        "test job",
        "writer",
    ],
    strong_title_keywords=[
        "backend",
        "php",
        "laravel",
        "application support",
        "technical support",
        "support engineer",
        "full stack",
        "full-stack",
        "software engineer",
        "web development intern",
    ],
    discouraged_title_keywords=[
        "devops",
        "platform engineer",
        "site reliability",
        "sre",
        "frontend",
        "react native",
        "ios",
        "penetration tester",
        "security",
        "designer",
        "qa",
        "quality assurance",
        "data analyst",
        "business analyst",
    ],
    junior_title_keywords=[
        "junior",
        "graduate",
        "entry",
        "entry-level",
        "new grad",
        "associate",
        "intern",
        "internship",
        "trainee",
    ],
    minimum_score=55,
)
