"""
Testet e Verifikimit të UI, Historikut dhe Shërbimeve të Smart Ghost Clipboard.
"""

import unittest
import os
import tempfile
import difflib

from app.storage.history_store import HistoryStore
from app.config import ACTION_CATEGORIES, PROMPT_CHIPS, PROMPTS
from app.ui_components.theme import Theme
from app.ui_components.diff_highlighter import DiffHighlighter


class TestGhostClipboard(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.store = HistoryStore(db_path=self.temp_db.name)

    def tearDown(self):
        try:
            os.remove(self.temp_db.name)
        except OSError:
            pass

    def test_history_store_crud(self):
        # 1. Shtimi
        entry_id = self.store.add_entry(
            action_name="✍️ Rregullo Gramatikën",
            original_text="Pershendetje si jeni",
            transformed_text="Përshëndetje, si jeni?",
            latency_ms=350,
        )
        self.assertIsNotNone(entry_id)

        # 2. Leximi
        entries = self.store.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action_name"], "✍️ Rregullo Gramatikën")
        self.assertFalse(entries[0]["is_favorite"])

        # 3. Toggle Favorite
        toggled = self.store.toggle_favorite(entry_id)
        self.assertTrue(toggled)
        entries_fav = self.store.get_entries(favorites_only=True)
        self.assertEqual(len(entries_fav), 1)
        self.assertTrue(entries_fav[0]["is_favorite"])

        # 4. Kërkimi me Search Query
        search_match = self.store.get_entries(search_query="Përshëndetje")
        self.assertEqual(len(search_match), 1)
        search_nomatch = self.store.get_entries(search_query="FjalaQeNukEkziston")
        self.assertEqual(len(search_nomatch), 0)

        # 5. Fshirja
        deleted = self.store.delete_entry(entry_id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.store.get_entries()), 0)

    def test_config_categories_and_prompts(self):
        self.assertIn("writing", ACTION_CATEGORIES)
        self.assertIn("business", ACTION_CATEGORIES)
        self.assertIn("translation", ACTION_CATEGORIES)
        self.assertIn("summary", ACTION_CATEGORIES)
        self.assertIn("code", ACTION_CATEGORIES)

        for cat_key, cat_data in ACTION_CATEGORIES.items():
            self.assertTrue(len(cat_data["actions"]) >= 5)
            for label, action_key, tooltip in cat_data["actions"]:
                self.assertIn(action_key, PROMPTS)

        self.assertTrue(len(PROMPT_CHIPS) >= 5)

    def test_diff_matcher_logic(self):
        orig = "Ky eshte nje test i thjeshte"
        trans = "Ky është një test shumë i thjeshtë"
        matcher = difflib.SequenceMatcher(None, orig.split(), trans.split())
        opcodes = matcher.get_opcodes()
        self.assertTrue(len(opcodes) > 0)

    def test_launcher_and_icon_assets(self):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(project_dir, "SmartGhostClipboard.exe")
        ico_path = os.path.join(project_dir, "app_icon.ico")
        self.assertTrue(os.path.isfile(exe_path), "SmartGhostClipboard.exe duhet të ekzistojë!")
        self.assertTrue(os.path.isfile(ico_path), "app_icon.ico duhet të ekzistojë!")
        self.assertGreater(os.path.getsize(exe_path), 10000, "Ekzekutuesi duhet të ketë madhësi valide.")
        self.assertGreater(os.path.getsize(ico_path), 5000, "Ikona ICO duhet të ketë të gjitha rezolucionet.")


if __name__ == "__main__":
    unittest.main()
