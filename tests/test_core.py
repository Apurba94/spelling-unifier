import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from spelling_unifier.cli import main
from spelling_unifier.core import dominant_style, find_variants, unify

MIXED = "We analysed the colour data. The color model was optimized and organised. We will analyze behaviours."


class FindTests(unittest.TestCase):
    def test_detects_both_styles(self):
        styles = {(w, s) for _, w, s, _ in find_variants(MIXED)}
        self.assertIn(("analysed", "uk"), styles)
        self.assertIn(("color", "us"), styles)
        self.assertIn(("optimized", "us-ize"), styles)
        self.assertIn(("organised", "uk-ise"), styles)
        self.assertIn(("behaviours", "uk"), styles)

    def test_ise_exceptions_untouched(self):
        self.assertEqual(find_variants("We advise, revise and exercise; a surprise promise. Wise otherwise."), [])

    def test_case_preserved(self):
        self.assertEqual(find_variants("Colour")[0][3], "Color")


class UnifyTests(unittest.TestCase):
    def test_to_us(self):
        new, changes = unify(MIXED, "us")
        self.assertEqual(new, "We analyzed the color data. The color model was optimized and organized. "
                              "We will analyze behaviors.")
        self.assertEqual(sum(changes.values()), 4)

    def test_to_uk_and_oxford(self):
        self.assertIn("optimised", unify(MIXED, "uk")[0])
        ox = unify(MIXED, "oxford")[0]
        self.assertIn("colour model", ox)
        self.assertIn("organized", ox)

    def test_majority(self):
        counts, major = dominant_style(find_variants("colour, behaviour, centre, color, organized"))
        self.assertEqual(major, "oxford")
        with self.assertRaises(ValueError):
            unify("x", "au")

    def test_cli_in_place(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "m.txt")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(MIXED)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main([p]), 1)
                main([p, "--to", "us", "--in-place"])
            with open(p, encoding="utf-8") as fh:
                self.assertNotIn("colour", fh.read())


if __name__ == "__main__":
    unittest.main()
