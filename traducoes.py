"""Interface translations. Engineering keys and dimension tables remain unchanged."""

TRANSLATIONS = {
    "Avaliação dimensional": "Dimensional assessment",
    "INTEGRIDADE · LIGAÇÕES FLANGEADAS": "INTEGRITY · FLANGED CONNECTIONS",
    "Avaliação dimensional de ligações flangeadas.": "Dimensional assessment of flanged connections.",
    "Medições claras. Decisões objetivas.": "Clear measurements. Objective decisions.",
    "FlangeCheck · versão 3.1 · Avaliação dimensional": "FlangeCheck · version 3.1 · Dimensional assessment",
    "ETAPA 01": "STEP 01",
    "Identifique a ligação": "Identify the connection",
    "Norma / série": "Standard / series",
    "Tipo de flange": "Flange type",
    "Diâmetro nominal · NPS (pol)": "Nominal diameter · NPS (in)",
    "Classe do flange": "Flange class",
    "Diâmetro nominal do estojo · automático": "Nominal stud diameter · automatic",
    "{diametro} mm · Definido por {norma}, NPS {nps} e classe {classe}.": "{diametro} mm · Defined by {norma}, NPS {nps} and class {classe}.",
    "O diâmetro nominal é automático. O diâmetro medido em campo deve ser informado na etapa 2.": "The nominal diameter is selected automatically. Enter the measured stud diameter in step 2.",
    "Fonte do diâmetro do estojo": "Stud diameter source",
    "Classe": "Class",
    "Diâmetro nominal do estojo obtido da furação, conforme a nota (a) da tabela: furo 1/8 pol maior que o estojo.": "Nominal stud diameter obtained from bolt-hole diameter per table note (a): hole 1/8 in larger than stud.",
    "Página {pagina} · coluna Stud Diameter.": "Page {pagina} · Stud Diameter column.",
    "Correlação consultada em 20/09/2026. O cadastro de avaliação B16.47 deste aplicativo contempla a Série A.": "Correlation consulted on 20 Sep 2026. The application's B16.47 assessment database covers Series A.",
    "O estojo desta combinação é {diametro}″. Os limites de avaliação do estojo e da porca ainda não estão cadastrados para esse tamanho. O diâmetro nominal está disponível, mas a avaliação dimensional fica indisponível até completar esses critérios.": "The stud for this combination is {diametro}″. Stud and nut assessment limits are not registered for this size. Nominal diameter is available, but dimensional assessment is disabled until these criteria are completed.",
    "Espessura do flange · tf": "Flange thickness · tf",
    "Diâmetro do estojo · D": "Stud diameter · D",
    "Altura da porca · H": "Nut height · H",
    "Largura da porca · F": "Nut width across flats · F",
    "ETAPA 02": "STEP 02",
    "Informe as medições": "Enter measurements",
    "Todas as medidas em milímetros. Preencha as quatro dimensões medidas em campo.": "All measurements in millimeters. Enter the four field measurements.",
    "Digite a medida": "Enter measurement",
    "Nominal": "Nominal",
    "Mínimo cadastrado": "Registered minimum",
    "Avaliar ligação": "Assess connection",
    "Preencha as quatro medições com valores maiores que zero para avaliar.": "Enter four measurements greater than zero to assess.",
    "Resultado da avaliação": "Assessment result",
    "NPS {nps} · Classe {classe} · Estojo {diametro}": "NPS {nps} · Class {classe} · Stud {diametro}",
    "APROVADO NO CRITÉRIO DIMENSIONAL · As quatro medidas atendem aos mínimos cadastrados.": "PASSES DIMENSIONAL CRITERIA · All four measurements meet registered minimums.",
    "REPROVADO NO CRITÉRIO DIMENSIONAL · Há medidas abaixo dos mínimos cadastrados.": "FAILS DIMENSIONAL CRITERIA · One or more measurements are below registered minimums.",
    "Conferência das dimensões": "Dimensional verification",
    "Atende ao mínimo": "Meets minimum",
    "Abaixo do mínimo": "Below minimum",
    "Medido": "Measured",
    "Mínimo": "Minimum",
    "Diferença": "Difference",
    "Preencha ou revise os dados e toque em Avaliar ligação para obter o resultado atualizado.": "Enter or review data and tap Assess connection to get an updated result.",
    "Como interpretar esta avaliação": "How to interpret this assessment",
    "A aprovação dimensional exige que as quatro medidas sejam iguais ou superiores aos limites cadastrados. A porca deve atender tanto à altura H quanto à largura F.": "Dimensional acceptance requires all four measurements to meet or exceed registered limits. The nut must meet both height H and width F limits.",
    "O valor nominal é a referência dimensional cadastrada. A aprovação usa o mínimo admissível; uma medida abaixo do nominal ainda pode atender ao critério.": "Nominal is the registered dimensional reference. Acceptance uses the allowable minimum; a measurement below nominal may still meet the criterion.",
    "Os valores de referência são os cadastrados nas tabelas deste aplicativo.": "Reference values are those registered in this application's tables.",
    "Flange não cadastrado para esta combinação.": "Flange not registered for this combination.",
    "Critérios de avaliação do estojo e da porca não cadastrados": "Stud and nut assessment criteria not registered",
    "Diâmetro do estojo não cadastrado para esta norma, NPS e classe.": "Stud diameter not registered for this standard, NPS and class.",
    "Norma/série do flange sem correlação cadastrada.": "Flange standard/series has no registered correlation."
}

FLANGE_TYPES = {
    "Soldado, Roscado, de Encaixe ou Cego": "Weld neck, threaded, socket weld or blind",
    "de Virola": "Lap joint",
    "Série A Cego": "Series A blind",
    "Série A Soldado": "Series A weld neck"
}


def traduzir(texto, idioma="pt"):
    return TRANSLATIONS.get(texto, texto) if idioma == "en" else texto


def nome_tipo(texto, idioma="pt"):
    if idioma != "en":
        return texto
    for origem, destino in FLANGE_TYPES.items():
        if texto.endswith(origem):
            return texto[:-len(origem)] + destino
    return texto
