import math
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
from avaliacao import avaliar, referencias, flanges

ROOT = Path(__file__).resolve().parent
TIPO = "ASME B16.5 Soldado, Roscado, de Encaixe ou Cego"


class FlangeCheckTests(unittest.TestCase):
    def test_referencias_nominais_e_minimas(self):
        refs = referencias('0,5 (½")', "150", TIPO)
        self.assertEqual([r["nominal"] for r in refs], [9.7, 12.7, 12.29, 21.91])
        self.assertEqual([r["minimo"] for r in refs], [7.76, 8.3, 6.1, 17.3])
        for f in flanges:
            try:
                refs = referencias(f["nps_pol"], f["classe"], f["tipo"])
            except ValueError:
                continue  # Diâmetros sem critérios já cobertos em test_estojos.
            self.assertTrue(all(r["nominal"] >= r["minimo"] > 0 for r in refs))

    def test_aprovacao_pelo_minimo_e_nao_pelo_nominal(self):
        resultado = avaliar('0,5 (½")', "150", TIPO, 8., 9., 7., 18.)
        self.assertTrue(resultado["aprovado"])
        self.assertTrue(all(d["medido"] < d["nominal"] for d in resultado["dimensoes"]))
        self.assertEqual(set(resultado), {"aprovado", "dimensoes"})
        for invalido in (None, 0., -1., math.inf, math.nan):
            with self.assertRaises(ValueError):
                avaliar('0,5 (½")', "150", TIPO, invalido, 9., 7., 18.)

    def test_interface_sem_sugestoes_e_com_nominais(self):
        for entrada in ("app.py", "appvisu.py"):
            app = AppTest.from_file(str(ROOT / entrada)).run()
            self.assertFalse(app.exception)
            self.assertEqual({x.key for x in app.selectbox}, {"norma", "tipo", "nps", "classe"})
            self.assertEqual(sum(c.value.startswith("Nominal:") for c in app.caption), 4)
            for w in app.number_input:
                w.set_value(100.)
            app.button(key="avaliar_ligacao").click().run()
            self.assertFalse(app.exception)
            texto = " ".join(x.value for tipo in (app.markdown, app.caption, app.subheader) for x in tipo)
            self.assertIn("FlangeCheck", texto)
            self.assertNotIn("RTI", texto)
            self.assertNotIn("Preservação", texto)
            cards = [m.value for m in app.markdown if m.value.startswith("Medido:")]
            self.assertEqual(len(cards), 4)
            self.assertTrue(all("Nominal:" in c and "Mínimo aceitável:" in c for c in cards))


if __name__ == "__main__":
    unittest.main()
