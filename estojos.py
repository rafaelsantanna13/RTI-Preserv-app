"""Consulta exata de diâmetros nominais por norma/série, NPS e classe.

Não interpola tabelas, não confunde diâmetro de furo com diâmetro do estojo
e não cria critérios de perda admissível para tamanhos sem cadastro.
"""
import json
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parent
with (BASE / "DiametrosEstojos.json").open(encoding="utf-8") as arquivo:
    CORRELACAO = json.load(arquivo)
with (BASE / "AvEstojosPorcas.json").open(encoding="utf-8") as arquivo:
    CRITERIOS = json.load(arquivo)

NORMAS_POR_TIPO = {
    "ASME B16.5 Soldado, Roscado, de Encaixe ou Cego": "ASME B16.5",
    "ASME B16.5 de Virola": "ASME B16.5",
    "ASME B16.47 Série A Cego": "ASME B16.47 Série A",
    "ASME B16.47 Série A Soldado": "ASME B16.47 Série A",
}


def fracao(valor):
    """Aceita frações mistas exatas, por exemplo '1 5/8'."""
    return sum((Fraction(parte) for parte in str(valor).split()), Fraction(0))


def norma_do_tipo(tipo):
    try:
        return NORMAS_POR_TIPO[tipo]
    except KeyError as erro:
        raise ValueError("Norma/série do flange sem correlação cadastrada.") from erro


def consultar_estojo(tipo, nps, classe):
    norma = norma_do_tipo(tipo)
    try:
        nps_num = Fraction(str(nps).split()[0].replace(",", "."))
        classe_chave = str(int(classe))
        # Rejeita classes fracionárias, sem arredondar para outra classe.
        if Fraction(str(classe)) != int(classe):
            raise ValueError
        tabela = CORRELACAO["diametros_pol"][norma][classe_chave]
        nps_chave = next(chave for chave in tabela if Fraction(chave) == nps_num)
        nominal = tabela[nps_chave]
    except (KeyError, ValueError, ZeroDivisionError, TypeError, IndexError, StopIteration) as erro:
        raise ValueError("Diâmetro do estojo não cadastrado para esta norma, NPS e classe.") from erro

    polegadas = fracao(nominal)
    criterios = next((e for e in CRITERIOS if
                      Fraction(e["diametro_nominal"].split()[0].replace(",", ".")) == polegadas), None)
    return {
        "norma": norma,
        "diametro_pol": nominal,
        "diametro_mm": float(polegadas * Fraction("25.4")),
        "diametro_nominal": criterios["diametro_nominal"] if criterios else f'{nominal}"',
        "criterios": criterios,
    }
