"""Regressões da interface. Execute: python -m unittest -v test_interface.py."""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from avaliacao import estojos, flanges, to_float
from estojos import consultar_estojo, norma_do_tipo

ROOT = Path(__file__).resolve().parent


class InterfaceTests(unittest.TestCase):
    def abrir(self, entrada="appvisu.py"):
        app = AppTest.from_file(str(ROOT / entrada)).run()
        self.assertFalse(app.exception)
        return app

    def limites(self, app):
        tipo, nps, classe = [app.selectbox(key=k).value for k in ("tipo", "nps", "classe")]
        diametro = consultar_estojo(tipo, nps, classe)["diametro_nominal"]
        flange = next(f for f in flanges if (f["tipo"], f["nps_pol"], f["classe"]) == (tipo, nps, classe))
        estojo = next(e for e in estojos if e["diametro_nominal"] == diametro)
        return [to_float(flange["tfmin_mm"]), estojo["d_min_b16_47"] if "B16.47" in tipo else estojo["d_min_b16_5"], estojo["H_min"], estojo["F_min"]]

    def preencher(self, app, valores):
        for i, valor in enumerate(valores):
            app.number_input(key=f"medida_{i}").set_value(valor)
        app.button(key="avaliar_ligacao").click().run()
        self.assertFalse(app.exception)

    def selecionar_tipo(self, app, tipo):
        app.selectbox(key="norma").set_value(norma_do_tipo(tipo)).run()
        app.selectbox(key="tipo").set_value(tipo).run()

    def test_entradas_e_campos_vazios(self):
        for entrada in ("app.py", "appvisu.py"):
            app = self.abrir(entrada)
            app.button(key="avaliar_ligacao").click().run()
            self.assertTrue(app.warning)
            self.assertFalse(app.success)
            self.assertFalse(app.error)

    def test_limites_e_reprovacao_individual(self):
        app = self.abrir()
        for tipo in sorted({f["tipo"] for f in flanges}):
            self.selecionar_tipo(app, tipo)
            limites = self.limites(app)
            self.preencher(app, limites)
            self.assertIn("APROVADO NO CRITÉRIO", app.success[0].value)
            for i in range(4):
                medidas = limites.copy()
                medidas[i] -= 0.01
                self.preencher(app, medidas)
                self.assertIn("REPROVADO NO CRITÉRIO", app.error[0].value)
                self.assertEqual(len(app.error), 2)

    def test_resultado_obsoleto_ao_alterar_medida(self):
        app = self.abrir()
        self.preencher(app, self.limites(app))
        app.number_input(key="medida_0").set_value(0.1).run()
        self.assertFalse(app.success)
        self.assertFalse(app.error)
        self.preencher(app, [0.1] * 4)
        self.assertIn("REPROVADO", app.error[0].value)

    def test_filtros_nao_oferecem_combinacoes_inexistentes(self):
        app = self.abrir()
        for tipo in sorted({f["tipo"] for f in flanges}):
            self.selecionar_tipo(app, tipo)
            for nps in list(app.selectbox(key="nps").options):
                app.selectbox(key="nps").set_value(nps).run()
                esperado = {f["classe"] for f in flanges if f["tipo"] == tipo and f["nps_pol"] == nps}
                self.assertEqual(set(app.selectbox(key="classe").options), esperado)
                self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
