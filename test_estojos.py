"""Correlação dimensional e integração: python -m unittest -v."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

from avaliacao import avaliar, flanges
from estojos import consultar_estojo, fracao, norma_do_tipo

B5 = "ASME B16.5 Soldado, Roscado, de Encaixe ou Cego"
A47 = "ASME B16.47 Série A Soldado"
ROOT = Path(__file__).resolve().parent


class CorrelacaoTests(unittest.TestCase):
    def test_valores_de_referencia_e_descontinuidades(self):
        # Valores das colunas Stud Diameter (Sigma, pp. 1-2), conferidos
        # com Texas Flange. NPS 22 vem da furação Texas, nota (a).
        exemplos = [
            (B5, "0,5 (½\")", "150", "1/2"),
            (B5, "2", "150", "5/8"),
            (B5, "2", "1500", "7/8"),
            (B5, "2", "2500", "1"),
            (B5, "8", "150", "3/4"),
            (B5, "8", "300", "7/8"),
            (B5, "8", "600", "1 1/8"),
            (B5, "2,5 (2½\")", "900", "1"),
            (B5, "3", "900", "7/8"),
            (B5, "22", "150", "1 1/4"),
            (B5, "22", "300", "1 1/2"),
            (B5, "22", "600", "1 5/8"),
            (B5, "24", "1500", "3 1/2"),
            (A47, "26", "150", "1 1/4"),
            (A47, "26", "300", "1 5/8"),
            (A47, "26", "600", "1 7/8"),
            (A47, "26", "900", "2 3/4"),
            (A47, "36", "300", "2"),
            (A47, "38", "300", "1 1/2"),
            (A47, "36", "600", "2 1/2"),
            (A47, "38", "600", "2 1/4"),
            (A47, "32", "900", "3 1/4"),
            (A47, "44", "900", "3 3/4"),
            (A47, "48", "900", "4"),
            (A47, "60", "600", "3 1/2"),
        ]
        for tipo, nps, classe, esperado in exemplos:
            with self.subTest(tipo=tipo, nps=nps, classe=classe):
                resultado = consultar_estojo(tipo, nps, classe)
                self.assertEqual(resultado["diametro_pol"], esperado)
                self.assertAlmostEqual(resultado["diametro_mm"], float(fracao(esperado)) * 25.4)

    def test_cobertura_do_cadastro_e_lacunas_de_criterios(self):
        chaves = set()
        sem_criterios = set()
        for flange in flanges:
            tipo, nps, classe = (flange[k] for k in ("tipo", "nps_pol", "classe"))
            resultado = consultar_estojo(tipo, nps, classe)
            chaves.add((norma_do_tipo(tipo), nps, classe))
            if resultado["criterios"] is None:
                sem_criterios.add((nps, classe, resultado["diametro_pol"]))
        self.assertEqual(len(chaves), 181)
        self.assertEqual(sem_criterios, {
            ("32", "900", "3 1/4"), ("44", "900", "3 3/4"),
            ("46", "900", "4"), ("48", "900", "4"),
            ("56", "600", "3 1/4"), ("58", "600", "3 1/4"),
        })

    def test_sem_interpolacao_ou_fallback_de_serie(self):
        for tipo, nps, classe in [
            (B5, "7", "150"), (B5, "22", "900"), (B5, "14", "2500"),
            (A47, "50", "900"), (A47, "26", "400"),
            ("ASME B16.47 Série B Soldado", "26", "150"),
            (B5, "0.50000001", "150"), (B5, "8", 150.1),
        ]:
            with self.subTest(tipo=tipo, nps=nps, classe=classe):
                with self.assertRaises(ValueError):
                    consultar_estojo(tipo, nps, classe)

    def test_calculo_usa_estojo_da_classe(self):
        # D=13 mm atende 3/4 pol na classe 150 (mínimo 12,4),
        # mas não 7/8 pol na classe 300 (mínimo 14,4).
        aprovado = avaliar("8", "150", B5, 100., 13., 100., 100.)
        reprovado = avaliar("8", "300", B5, 100., 13., 100., 100.)
        self.assertTrue(aprovado["aprovado"])
        self.assertFalse(reprovado["aprovado"])
        with self.assertRaisesRegex(ValueError, "não cadastrados"):
            avaliar("48", "900", A47, 300., 300., 300., 300.)



class AutomaticoInterfaceTests(unittest.TestCase):
    def abrir(self):
        app = AppTest.from_file(str(ROOT / "appvisu.py")).run()
        self.assertFalse(app.exception)
        return app

    def test_troca_classe_atualiza_estojo_limites_e_resultado(self):
        app = self.abrir()
        app.selectbox(key="tipo").set_value(B5).run()
        app.selectbox(key="nps").set_value("8").run()
        self.assertEqual(app.metric[0].value, "3/4″")
        self.assertNotIn("estojo", [s.key for s in app.selectbox])
        for widget in app.number_input:
            widget.set_value(100.)
        app.button[0].click().run()
        self.assertTrue(app.success)
        app.selectbox(key="classe").set_value("300").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "7/8″")
        self.assertFalse(app.success)
        self.assertTrue(any("14,40 mm" in c.value for c in app.caption))
        app.selectbox(key="norma").set_value("ASME B16.47 Série A").run()
        self.assertEqual(app.metric[0].value, "1 5/8″")
        self.assertFalse(app.exception)

    def test_criterios_ausentes_sem_aprovacao_e_recuperacao(self):
        app = self.abrir()
        app.selectbox(key="norma").set_value("ASME B16.47 Série A").run()
        app.selectbox(key="nps").set_value("48").run()
        for widget in app.number_input:
            widget.set_value(300.)
        app.button[0].click().run()
        self.assertTrue(app.success)
        app.selectbox(key="classe").set_value("900").run()
        self.assertEqual(app.metric[0].value, "4″")
        self.assertFalse(app.exception)
        self.assertFalse(app.success)
        self.assertFalse(app.button)
        self.assertTrue(any("não estão cadastrados" in w.value for w in app.warning))
        app.selectbox(key="classe").set_value("150").run()
        self.assertFalse(app.exception)
        self.assertTrue(app.button)
        self.assertEqual(app.metric[0].value, "1 1/2″")


if __name__ == "__main__":
    unittest.main()
