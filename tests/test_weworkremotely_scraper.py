import unittest
from unittest.mock import Mock, patch

from scrapers.weworkremotely import WeWorkRemotelyScraper


class WeWorkRemotelyScraperTest(unittest.TestCase):
    @patch("scrapers.weworkremotely.requests.get")
    def test_parses_rss_feed(self, mock_get: Mock) -> None:
        mock_get.return_value = Mock(
            status_code=200,
            text="""
                <rss version="2.0">
                  <channel>
                    <item>
                      <title>Example Co: Junior Backend Developer</title>
                      <link>https://example.com/jobs/1</link>
                      <description><![CDATA[
                        <p><strong>Headquarters:</strong> Singapore</p>
                        <p>Build APIs with PHP and Laravel</p>
                      ]]></description>
                      <pubDate>Fri, 27 Jun 2026 10:00:00 GMT</pubDate>
                      <category>Worldwide</category>
                    </item>
                  </channel>
                </rss>
            """,
        )
        scraper = WeWorkRemotelyScraper()

        jobs = scraper.fetch_jobs()

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].title, "Junior Backend Developer")
        self.assertEqual(jobs[0].company, "Example Co")
        self.assertEqual(jobs[0].country, "Singapore")
        self.assertEqual(jobs[0].source, "WeWorkRemotely")


if __name__ == "__main__":
    unittest.main()
