"""Regressions for the bilingual UI (run with python -m unittest -v)."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from traducoes import traduzir

ROOT = Path(__file__).resolve().parent


class LanguageTests(unittest.TestCase):
    def test_translations(self):
        self.assertEqual(traduzir("Avaliar ligação", "en"), "Assess connection")
        self.assertEqual(traduzir("Avaliar ligação", "pt"), "Avaliar ligação")
        self.assertEqual(traduzir("APROVADO NO CRITÉRIO DIMENSIONAL · As quatro medidas atendem aos mínimos cadastrados.", "en"),
                         "PASSES DIMENSIONAL CRITERIA · All four measurements meet registered minimums.")

    def test_flag_switch_keeps_dimensions(self):
        app = AppTest.from_file(str(ROOT / "appvisu.py")).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.get("segmented_control")[0].value, "pt")
        self.assertEqual(app.button(key="avaliar_ligacao").label, "Avaliar ligação")
        original = app.metric[0].value
        for widget in app.number_input:
            widget.set_value(100.)
        app.button(key="avaliar_ligacao").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.success)
        app.get("segmented_control")[0].set_value("en").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, original)
        self.assertEqual(app.button(key="avaliar_ligacao").label, "Assess connection")
        self.assertTrue(any("PASSES DIMENSIONAL CRITERIA" in item.value for item in app.success))
        app.get("segmented_control")[0].set_value("pt").run()
        self.assertEqual(app.button(key="avaliar_ligacao").label, "Avaliar ligação")
        self.assertTrue(any("APROVADO NO CRITÉRIO" in item.value for item in app.success))


if __name__ == "__main__":
    unittest.main()
