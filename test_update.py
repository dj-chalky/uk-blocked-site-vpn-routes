import tempfile
import unittest
from pathlib import Path
import update


class SubscriptionTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(update.domain('https://WWW.Example.COM/forum?q=1'), 'example.com')
        self.assertEqual(update.domain('https://szcz.itch.io/game'), 'szcz.itch.io')
        self.assertEqual(update.domain('4chan.org'), '4chan.org')
        self.assertEqual(update.domain(update.domain('www.www.example.com')), 'example.com')
        self.assertEqual(update.domain('https://bücher.de/'), 'xn--bcher-kva.de')
        for bad in ('<html>Error</html>', 'bad domain.com', 'foo..com', '-bad.com'):
            with self.assertRaises(ValueError):
                update.domain(bad)

    def test_heading_extraction_excludes_evidence_links(self):
        parser = update.SiteHeadings()
        parser.feed('<h3><a href="https://example.com/path">Name</a></h3><a href="https://evidence.org">Announcement</a>')
        self.assertEqual(parser.urls, ['https://example.com/path'])

    def test_court_extraction(self):
        parser = update.CourtPage()
        parser.feed('<a href="/site/http://example.com">Site report</a><a href="/legal-blocks/sites/gb/63?sort=url" aria-label="Last">Last</a>')
        self.assertEqual(parser.urls, ['http://example.com'])
        self.assertIn('/63?', parser.last)

    def test_error_page_rejected(self):
        with self.assertRaises(ValueError):
            update.parse_sources('<html>server error</html>', '<html>error</html>')

    def test_source_loss_preserves_published_file(self):
        old_root = update.ROOT
        with tempfile.TemporaryDirectory(dir=update.ROOT) as directory:
            update.ROOT = Path(directory)
            try:
                targets = {f'a{i}.example.com' for i in range(20)}
                update.build({'osatracker': targets, 'blocked-osa': targets})
                before = (update.ROOT / 'domains.txt').read_bytes()
                with self.assertRaises(ValueError):
                    update.build({'osatracker': set(), 'blocked-osa': targets})
                self.assertEqual((update.ROOT / 'domains.txt').read_bytes(), before)
                self.assertFalse(before.startswith(b'\xef\xbb\xbf'))
                self.assertNotIn(b'\r', before)
            finally:
                update.ROOT = old_root


if __name__ == '__main__':
    unittest.main()
