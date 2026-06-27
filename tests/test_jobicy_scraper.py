import unittest
from unittest.mock import Mock, patch

from scrapers.jobicy import JobicyScraper


class JobicyScraperTest(unittest.TestCase):
    @patch("scrapers.jobicy.requests.get")
    def test_parses_json_api(self, mock_get: Mock) -> None:
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "success": True,
                "jobs": [
                    {
                        "id": 12345,
                        "url": "https://example.com/jobs/1",
                        "jobTitle": "Technical Support Engineer",
                        "companyName": "Strikingly",
                        "jobDescription": "Provide technical support.",
                        "pubDate": "2026-06-27 12:00:00",
                        "salaryMin": 50000,
                        "salaryMax": 60000,
                        "salaryCurrency": "USD",
                        "salaryPeriod": "yearly",
                        "jobGeo": "Worldwide",
                    }
                ],
            },
        )
        scraper = JobicyScraper()
        jobs = scraper.fetch_jobs()

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, "Technical Support Engineer")
        self.assertEqual(jobs[0].company, "Strikingly")
        self.assertEqual(jobs[0].salary, "50000 - 60000 USD/yearly")
        self.assertEqual(jobs[0].source, "Jobicy")

    @patch("scrapers.jobicy.requests.get")
    def test_returns_empty_on_api_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = Exception("Connection error")
        jobs = JobicyScraper().fetch_jobs()
        self.assertEqual(jobs, [])

    @patch("scrapers.jobicy.requests.get")
    def test_returns_empty_on_missing_jobs_key(self, mock_get: Mock) -> None:
        mock_get.return_value = Mock(status_code=200, json=lambda: {"success": True})
        jobs = JobicyScraper().fetch_jobs()
        self.assertEqual(jobs, [])


if __name__ == "__main__":
    unittest.main()

