"""Avaliação exclusivamente dimensional do FlangeCheck."""
import json
import math
from pathlib import Path
from estojos import consultar_estojo

BASE = Path(__file__).resolve().parent


def carregar(nome):
    with (BASE / nome).open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


flanges = carregar("AvFlanges.json")
estojos = carregar("AvEstojosPorcas.json")


def to_float(x):
    return float(str(x).replace(",", "."))


def referencias(nps, classe, tipo):
    """Mesmas referências para os campos da tela e para o cálculo."""
    flange = next((f for f in flanges if
                   (f["nps_pol"], f["classe"], f["tipo"]) == (nps, classe, tipo)), None)
    if flange is None:
        raise ValueError("Flange não cadastrado para esta combinação.")
    selecao = consultar_estojo(tipo, nps, classe)
    estojo = selecao["criterios"]
    if estojo is None:
        raise ValueError("Critérios de avaliação do estojo e da porca não cadastrados")
    return [
        {"nome": "Espessura do flange · tf", "nominal": to_float(flange["tf_flange_mm"]),
         "minimo": to_float(flange["tfmin_mm"])},
        {"nome": "Diâmetro do estojo · D", "nominal": selecao["diametro_mm"],
         "minimo": estojo["d_min_b16_47"] if "B16.47" in tipo else estojo["d_min_b16_5"]},
        {"nome": "Altura da porca · H", "nominal": estojo["H_nom"], "minimo": estojo["H_min"]},
        {"nome": "Largura da porca · F", "nominal": estojo["F_nom"], "minimo": estojo["F_min"]},
    ]


def avaliar(nps, classe, tipo, tf_med, d_med, h_med, f_med):
    refs = referencias(nps, classe, tipo)
    medidas = (tf_med, d_med, h_med, f_med)
    if any(m is None or not math.isfinite(m) or m <= 0 for m in medidas):
        raise ValueError("Preencha as quatro medições com valores finitos maiores que zero.")
    dimensoes = [dict(ref, medido=medido, aprovado=medido >= ref["minimo"])
                 for ref, medido in zip(refs, medidas)]
    return {"aprovado": all(d["aprovado"] for d in dimensoes), "dimensoes": dimensoes}
