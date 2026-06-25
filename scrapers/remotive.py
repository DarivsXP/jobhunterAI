import requests

def get_jobs():

    url = "https://remotive.com/api/remote-jobs"

    data = requests.get(url).json()

    jobs = []

    for item in data["jobs"]:

        jobs.append({
            "title": item["title"],
            "company": item["company_name"],
            "url": item["url"],
            "description": item["description"],
            "posted_at": item["publication_date"],
            "source": "Remotive"
        })

    return jobs