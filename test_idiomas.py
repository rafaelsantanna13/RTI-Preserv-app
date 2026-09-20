"""Regressions for the bilingual UI (run with python -m unittest -v)."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from traducoes import traduzir, nome_tipo, nome_norma

ROOT = Path(__file__).resolve().parent


class LanguageTests(unittest.TestCase):
    def test_translations(self):
        self.assertEqual(traduzir("Avaliar ligação", "en"), "Assess connection")
        self.assertEqual(traduzir("Avaliar ligação", "pt"), "Avaliar ligação")
        self.assertEqual(traduzir("APROVADO NO CRITÉRIO DIMENSIONAL · As quatro medidas atendem aos mínimos cadastrados.", "en"),
                         "PASSES DIMENSIONAL CRITERIA · All four measurements meet registered minimums.")

    def test_flange_type_translation_and_canonical_keys(self):
        casos = {
            "ASME B16.5 Soldado, Roscado, de Encaixe ou Cego": "Weld neck, threaded, socket weld or blind",
            "ASME B16.5 de Virola": "Lap joint",
            "ASME B16.47 Série A Cego": "Blind",
            "ASME B16.47 Série A Soldado": "Weld neck",
        }
        for chave, ingles in casos.items():
            with self.subTest(tipo=chave):
                self.assertEqual(nome_tipo(chave, "en"), ingles)
                self.assertNotEqual(nome_tipo(chave, "pt"), ingles)
        self.assertEqual(nome_norma("ASME B16.47 Série A", "en"), "ASME B16.47 Series A")

    def test_language_switch_rebuilds_type_selector(self):
        app = AppTest.from_file(str(ROOT / "appvisu.py")).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="tipo").value,
                         "ASME B16.5 Soldado, Roscado, de Encaixe ou Cego")
        app.get("segmented_control")[0].set_value("en").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="tipo_en").value,
                         "ASME B16.5 Soldado, Roscado, de Encaixe ou Cego")
        app.selectbox(key="norma").set_value("ASME B16.47 Série A").run()
        self.assertFalse(app.exception)
        app.selectbox(key="tipo_en").set_value("ASME B16.47 Série A Soldado").run()
        self.assertFalse(app.exception)
        app.get("segmented_control")[0].set_value("pt").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="tipo").value, "ASME B16.47 Série A Soldado")

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
