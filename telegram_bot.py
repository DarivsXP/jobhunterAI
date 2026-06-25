def send_hot_match(job, result):

    message = f"""
🔥 APPLY IMMEDIATELY

Role:
{job['title']}

Company:
{job['company']}

Score:
{result['score']}

Skills:
{', '.join(result['skills'])}

Apply:
{job['url']}
"""

    send_message(message)


def send_strong_match(job, result):

    message = f"""
⭐ HIGH PRIORITY

Role:
{job['title']}

Company:
{job['company']}

Score:
{result['score']}

Apply:
{job['url']}
"""

    send_message(message)