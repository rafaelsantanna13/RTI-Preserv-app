"""Consultas dimensionais e RTI com os critérios originais do projeto."""
import json
from pathlib import Path
from estojos import consultar_estojo

BASE = Path(__file__).resolve().parent

def carregar(nome):
    with (BASE / nome).open(encoding="utf-8") as arquivo:
        return json.load(arquivo)

flanges = carregar("AvFlanges.json")
estojos = carregar("AvEstojosPorcas.json")
rti = carregar("ClasseRTI.json")

def to_float(x):
    return float(str(x).replace(",", "."))

def avaliar(nps, classe, tipo, mat_f, mat_e, fluido, hist, perda,
            tf_med, d_med, h_med, f_med):

    # buscar flange
    flange = next((f for f in flanges if f["nps_pol"] == nps and f["classe"] == classe and f["tipo"] == tipo), None)

    # O diâmetro nominal é determinado pelo flange também no cálculo,
    # sem aceitar uma seleção manual incompatível com a norma/NPS/classe.
    try:
        estojo = consultar_estojo(tipo, nps, classe)["criterios"]
    except ValueError as erro:
        return str(erro)

    if not flange:
        return "Erro nos dados"
    if not estojo:
        return "Critérios de avaliação do estojo e da porca não cadastrados"

    tf_min = to_float(flange["tfmin_mm"])

    if "B16.47" in tipo:
        d_min = estojo["d_min_b16_47"]
    else:
        d_min = estojo["d_min_b16_5"]

    flange_ok = tf_med >= tf_min
    estojo_ok = d_med >= d_min
    porca_ok = (h_med >= estojo["H_min"] and f_med >= estojo["F_min"])

    aprovado = "Sim" if (flange_ok and estojo_ok and porca_ok) else "Não"

    # RTI
    linha = next((r for r in rti if
        r["material_do_flange"] == mat_f and
        r["material_do_estojo"] == mat_e and
        r["fluido"] == fluido and
        r["historico_do_sistema"] == hist and
        r["possui_perda_de_massa"] == perda and
        r["aprovado_no_criterio"] == aprovado), None)

    if linha:
        return f'RTI: {linha["classificacao_rti"]}\nPreservação: {linha["preservacao"]}'
    else:
        return "RTI não encontrada"
