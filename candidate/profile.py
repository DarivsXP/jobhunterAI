"""
Candidate Profile

This file represents YOU.

Every AI feature will read from this profile.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class CandidateProfile:

    # Basic Information

    name: str

    experience_level: str

    portfolio: str

    github: str

    linkedin: str

    # Job Preferences

    preferred_roles: list[str] = field(default_factory=list)

    preferred_skills: list[str] = field(default_factory=list)

    preferred_countries: list[str] = field(default_factory=list)

    excluded_titles: list[str] = field(default_factory=list)

    minimum_score: int = 55


MY_PROFILE = CandidateProfile(

    name="Darivs Egipto",

    experience_level="Junior",

    portfolio="https://www.cyrilegipto.space",

    github="https://github.com/DarivsXP",

    linkedin="",

    preferred_roles=[

        "Junior Software Engineer",

        "Junior Backend Developer",

        "Junior Full Stack Developer",

        "PHP Developer",

        "Laravel Developer",

        "Backend Developer",

        "Software Developer",

        "Application Support Engineer",

        "Technical Support Engineer",

        "Customer Support Engineer",

    ],

    preferred_skills=[

        "PHP",

        "Laravel",

        "Python",

        "MySQL",

        "PostgreSQL",

        "SQLite",

        "JavaScript",

        "HTML",

        "CSS",

        "Git",

        "GitHub",

        "REST API",

    ],

    preferred_countries=[

        "Australia",

        "Canada",

        "United Kingdom",

        "UK",

        "New Zealand",

        "Singapore",

        "Worldwide",

    ],

    excluded_titles=[

        "Senior",

        "Staff",

        "Lead",

        "Principal",

        "Architect",

        "Manager",

        "Director",

        "Head",

        "VP",

    ],

    minimum_score=55,

)