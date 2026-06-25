from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_cover_letter(job):

    prompt = f"""
Write a SHORT cover letter.

Rules:

- Maximum 120 words
- Simple
- Direct
- Mention portfolio:
www.cyrilegipto.space
- Encourage recruiter to
review portfolio
- No fluff

Job Title:
{job['title']}

Company:
{job['company']}

Description:
{job['description']}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return (
        response
        .choices[0]
        .message
        .content
    )