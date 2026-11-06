import pathlib, sys, unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "app"))
from i18n import LocalizedHTML, TRANSLATIONS


class LanguageTests(unittest.TestCase):
    def test_svg_preserves_self_closing_paths_and_viewbox(self):
        s = '<html lang="ko"><svg viewBox="0 0 10 10"><path d="M0 0"/><path d="M1 1"/></svg><h1>환경 안내서</h1></html>'
        p = LocalizedHTML("en")
        p.feed(s)
        r = "".join(p.parts)
        self.assertIn("viewBox=", r)
        self.assertEqual(r.count("/>"), 2)
        self.assertIn("Environment sheet", r)

    def test_translation_keys_match(self):
        self.assertEqual(set(TRANSLATIONS["ko"]), set(TRANSLATIONS["en"]))


if __name__ == "__main__":
    unittest.main()
