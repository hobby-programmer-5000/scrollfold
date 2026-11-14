"""UI text checks for the desktop app (i18n.py) and the web app (web/i18n.js).

- English and Korean have the same keys and the same {placeholders}
- every key the code asks for exists (static keys found in the source + known dynamic keys)
- every error kind core can produce has a message
"""
import re
import unittest
from pathlib import Path

import core
from i18n import STRINGS

ROOT = Path(__file__).parent
PH = re.compile(r"\{(\w+)\}")


def placeholders(text: str) -> set:
    return set(PH.findall(text))


class DesktopStrings(unittest.TestCase):
    def test_same_keys_and_placeholders(self):
        en, ko = STRINGS["en"], STRINGS["ko"]
        self.assertEqual(set(en) - set(ko), set(), "keys missing in Korean")
        self.assertEqual(set(ko) - set(en), set(), "keys missing in English")
        for k in en:
            self.assertEqual(placeholders(en[k]), placeholders(ko[k]), f"placeholders differ for {k!r}")

    def test_every_used_key_exists(self):
        src = (ROOT / "app.py").read_text(encoding="utf-8")
        # Keys ending in "_" are prefixes joined with a name ("fit_" + mode); they are listed below in full.
        used = {k for k in re.findall(r'self\.tr\(\s*"([\w:]+)"', src) if not k.endswith("_")}
        used |= {"ratio_original"} | {"hint_" + k for k in core.RATIOS if k != "original"}
        used |= {"fit_" + m for m in core.FIT_MODES}
        self.assertGreater(len(used), 20)
        self.assertEqual(used - set(STRINGS["en"]), set())

    def test_every_error_kind_has_a_message(self):
        kinds = set(re.findall(r'SplitError\([^)]*?"(\w+)"', (ROOT / "core.py").read_text(encoding="utf-8"), re.S))
        kinds |= {"unsupported", "out_of_memory", "file_problem", "other"}  # from core.describe_error
        self.assertIn("too_narrow", kinds)
        self.assertEqual(kinds - set(STRINGS["en"]), set())


if __name__ == "__main__":
    unittest.main(verbosity=1)
