import unittest
from unittest.mock import Mock, patch

from scrapers.himalayas import HimalayasScraper


class HimalayasScraperTest(unittest.TestCase):
    @patch("scrapers.himalayas.requests.get")
    def test_parses_rss_feed(self, mock_get: Mock) -> None:
        mock_get.return_value = Mock(
            status_code=200,
            text="""
                <rss xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
                  <channel>
                    <item>
                      <title>Junior Backend Developer</title>
                      <link>https://example.com/jobs/1</link>
                      <description><![CDATA[Build APIs with PHP and Laravel]]></description>
                      <pubDate>Fri, 27 Jun 2026 10:00:00 GMT</pubDate>
                      <himalayasJobs:companyName>Example Co</himalayasJobs:companyName>
                      <himalayasJobs:locationRestriction>Singapore</himalayasJobs:locationRestriction>
                    </item>
                  </channel>
                </rss>
            """,
        )
        scraper = HimalayasScraper()

        jobs = scraper.fetch_jobs()

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, "Junior Backend Developer")
        self.assertEqual(jobs[0].company, "Example Co")
        self.assertEqual(jobs[0].country, "Singapore")
        self.assertEqual(jobs[0].source, "Himalayas")


if __name__ == "__main__":
    unittest.main()
