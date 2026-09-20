"""Interface compartilhada pelas duas entradas do Streamlit."""

import streamlit as st
from pathlib import Path

from avaliacao import avaliar, referencias, flanges, to_float
from estojos import CORRELACAO, consultar_estojo, norma_do_tipo
from traducoes import traduzir, nome_tipo, nome_norma


BASE_DIR = Path(__file__).resolve().parent


def caminho_imagem_medicao(idioma):
    """Imagem ilustrativa escolhida pelo idioma; sem alterar critérios dimensionais."""
    nome = "dimensoes_medicao_en.png" if idioma == "en" else "dimensoes_medicao_pt.png"
    return BASE_DIR / "assets" / nome


def numero(valor):
    return f"{valor:.2f}".replace(".", "," if st.session_state.get("idioma", "pt") == "pt" else ".")


def t(texto):
    return traduzir(texto, st.session_state.get("idioma", "pt"))


def exibir_nps(valor, idioma):
    """Traduz apenas a vírgula decimal do rótulo; a chave técnica é preservada."""
    return valor.replace(",", ".") if idioma == "en" else valor


def ordem_nps(valor):
    return to_float(valor.split()[0])


def selecionar(label, opcoes, key, **kwargs):
    # Evita manter uma classe/NPS inválida após a troca do tipo de flange.
    if st.session_state.get(key) not in opcoes:
        st.session_state[key] = opcoes[0]
    return st.selectbox(label, opcoes, key=key, **kwargs)


def main():
    st.set_page_config(page_title="FlangeCheck", page_icon="🔩", layout="centered")
    # Reserva uma faixa vazia para a barra fixa do Streamlit no celular.
    # O seletor deve começar abaixo da área ocupada por Share/Manage app.
    st.markdown('<div aria-hidden="true" style="height: 80px;"></div>',
                unsafe_allow_html=True)
    # Um único controle horizontal evita que duas colunas empilhem no celular.
    if "idioma" not in st.session_state:
        st.session_state["idioma"] = "pt"
    idioma = st.segmented_control(
        "Idioma / Language",
        options=["pt", "en"],
        format_func=lambda valor: "🇧🇷 Português" if valor == "pt" else "🇺🇸 English",
        default=st.session_state["idioma"],
        selection_mode="single",
        key="seletor_idioma",
        label_visibility="collapsed",
        width="stretch",
    )
    if idioma is not None:
        st.session_state["idioma"] = idioma
    st.markdown("""
    <style>
    .block-container {max-width: 960px; padding-top: 2rem; padding-bottom: 3rem;}
    .fc-hero {background: #142c43; color: #fff; padding: 28px;
        border-radius: 18px; margin-bottom: 24px; border-top: 5px solid #36c3b2;}
    .fc-hero .eyebrow {font-size: .72rem; font-weight: 700;
        letter-spacing: .12em; color: #8fdfd5; margin-bottom: 10px;}
    .fc-hero h1 {font-size: 2rem; line-height: 1.15; color: #fff;
        padding: 0; margin: 0 0 12px; font-weight: 750;}
    .fc-hero p {color: #d4e1ec; font-size: .95rem; line-height: 1.6; margin: 0;}
    .fc-step {color: #087f8c; font-size: .75rem; font-weight: 700;
        letter-spacing: .08em; margin-bottom: 4px;}
    @media (max-width: 640px) {
        .block-container {padding: 1.4rem 1rem 2rem;}
        .fc-hero {padding: 22px 20px;}
        .fc-hero h1 {font-size: 1.7rem;}
    }
    </style>
    <div class="fc-hero">
      <div class="eyebrow">{eyebrow}</div>
      <h1>FlangeCheck</h1>
      <p>{descricao}<br>{subtitulo}</p>
    </div>
    """.replace("{eyebrow}", t("INTEGRIDADE · LIGAÇÕES FLANGEADAS"))
       .replace("{descricao}", t("Avaliação dimensional de ligações flangeadas."))
       .replace("{subtitulo}", t("Medições claras. Decisões objetivas.")), unsafe_allow_html=True)
    st.caption(t("FlangeCheck · versão 3.1 · Avaliação dimensional"))

    with st.container(border=True):
        st.markdown(f'<div class="fc-step">{t("ETAPA 01")}</div>', unsafe_allow_html=True)
        st.subheader(t("Identifique a ligação"))
        norma = selecionar(
            t("Norma / série"), ["ASME B16.5", "ASME B16.47 Série A"], "norma",
            format_func=lambda valor: nome_norma(valor, st.session_state["idioma"]),
        )
        tipos_disponiveis = sorted({f["tipo"] for f in flanges
                                   if norma_do_tipo(f["tipo"]) == norma})
        # Chaves distintas por idioma obrigam o Streamlit a reconstruir as
        # opções traduzidas (inclusive o valor já selecionado) no navegador.
        # O valor técnico permanece em português, como nas tabelas de engenharia.
        idioma_atual = st.session_state["idioma"]
        chave_tipo = "tipo" if idioma_atual == "pt" else "tipo_en"
        tipo_anterior = st.session_state.get("tipo_canonico")
        if tipo_anterior not in tipos_disponiveis:
            tipo_anterior = tipos_disponiveis[0]
        if (st.session_state.get("idioma_tipo_anterior") != idioma_atual
                or st.session_state.get(chave_tipo) not in tipos_disponiveis):
            st.session_state[chave_tipo] = tipo_anterior
        tipo = selecionar(
            t("Tipo de flange"), tipos_disponiveis, chave_tipo,
            format_func=lambda valor: nome_tipo(valor, idioma_atual),
        )
        st.session_state["tipo_canonico"] = tipo
        st.session_state["idioma_tipo_anterior"] = idioma_atual
        disponiveis = [f for f in flanges if f["tipo"] == tipo]
        c1, c2 = st.columns(2)
        with c1:
            opcoes_nps = sorted({f["nps_pol"] for f in disponiveis}, key=ordem_nps)
            chave_nps = "nps" if idioma_atual == "pt" else "nps_en"
            nps_anterior = st.session_state.get("nps_canonico")
            if nps_anterior not in opcoes_nps:
                nps_anterior = opcoes_nps[0]
            if (st.session_state.get("idioma_nps_anterior") != idioma_atual
                    or st.session_state.get(chave_nps) not in opcoes_nps):
                st.session_state[chave_nps] = nps_anterior
            nps = selecionar(
                t("Diâmetro nominal · NPS (pol)"), opcoes_nps, chave_nps,
                format_func=lambda valor: exibir_nps(valor, idioma_atual),
            )
            st.session_state["nps_canonico"] = nps
            st.session_state["idioma_nps_anterior"] = idioma_atual
        with c2:
            classe = selecionar(t("Classe do flange"),
                                sorted({f["classe"] for f in disponiveis if f["nps_pol"] == nps}, key=int), "classe")
        try:
            selecao = consultar_estojo(tipo, nps, classe)
        except ValueError as erro:
            st.session_state.pop("avaliacao_atual", None)
            st.error(t(str(erro)))
            st.stop()
        diametro = selecao["diametro_nominal"]
        st.metric(t("Diâmetro nominal do estojo · automático"), f'{selecao["diametro_pol"]}″')
        st.caption(t("{diametro} mm · Definido por {norma}, NPS {nps} e classe {classe}.").format(diametro=numero(selecao["diametro_mm"]), norma=nome_norma(norma, idioma_atual), nps=exibir_nps(nps, idioma_atual), classe=classe))
        st.caption(t("O diâmetro nominal é automático. O diâmetro medido em campo deve ser informado na etapa 2."))
        with st.expander(t("Norma de referência")):
            st.markdown(f"**{norma}**")
        with st.expander(t("Referências dos valores mínimos aceitáveis")):
            st.markdown(
                "1. **Brown, W.; Long, S. (2017).** "
                "[Acceptable Levels of Corrosion for Pressure Boundary Bolted Joints]"
                "(https://doi.org/10.1115/PVP2017-65507). "
                "**ASME 2017 Pressure Vessels and Piping Conference (PVP 2017).** "
                "Paper No. **PVP2017-65507**. "
                "DOI: 10.1115/PVP2017-65507.\\n\\n"
                "2. **Brown, W.; Long, S. (2018).** "
                "[Update on Allowable Limits for Corroded Pressure Boundary Bolted Joints]"
                "(https://doi.org/10.1115/PVP2018-85005). "
                "**ASME 2018 Pressure Vessels and Piping Conference (PVP 2018).** "
                "Paper No. **PVP2018-85005**. "
                "DOI: 10.1115/PVP2018-85005."
            )
            st.caption(t("Referências técnicas da avaliação de corrosão. Os limites numéricos utilizados são os cadastrados no aplicativo; a correspondência de cada valor com os artigos não foi verificada nesta revisão."))

    estojo = selecao["criterios"]
    if estojo is None:
        st.session_state.pop("avaliacao_atual", None)
        st.warning(t("O estojo desta combinação é {diametro}″. Os limites de avaliação do estojo e da porca ainda não estão cadastrados para esse tamanho. O diâmetro nominal está disponível, mas a avaliação dimensional fica indisponível até completar esses critérios.").format(diametro=selecao["diametro_pol"]))
        st.stop()

    refs = referencias(nps, classe, tipo)
    limites = [ref["minimo"] for ref in refs]
    nominais = [ref["nominal"] for ref in refs]
    labels = [t("Espessura do flange · tf"), t("Diâmetro do estojo · D"),
              t("Altura da porca · H"), t("Largura da porca · F")]
    medidas = []
    with st.container(border=True):
        st.markdown(f'<div class="fc-step">{t("ETAPA 02")}</div>', unsafe_allow_html=True)
        st.subheader(t("Informe as medições"))
        st.caption(t("Todas as medidas em milímetros. Preencha as quatro dimensões medidas em campo."))
        with st.expander(t("Guia visual das medições"), expanded=True):
            st.caption(t("Identifique no desenho as dimensões tf, D, H e F antes de medir."))
            imagem = caminho_imagem_medicao(st.session_state.get("idioma", "pt"))
            if imagem.is_file():
                st.image(
                    str(imagem),
                    caption=t("Dimensões do flange, estojo e porca (ilustração esquemática)."),
                    use_container_width=True,
                )
            else:
                st.caption(t("O desenho neste idioma estará disponível em breve."))
        for inicio in (0, 2):
            colunas = st.columns(2)
            for i in range(inicio, inicio + 2):
                with colunas[i - inicio]:
                    medidas.append(st.number_input(
                        labels[i] + " (mm)", min_value=0.0, value=None,
                        step=0.1, format="%.2f", placeholder=t("Digite a medida"),
                        key=f"medida_{i}"))
                    st.caption(f'{t("Nominal")}: **{numero(nominais[i])} mm**')
                    st.caption(f'{t("Mínimo aceitável")}: **{numero(limites[i])} mm**')

    assinatura = ("FlangeCheck-3", tipo, nps, classe, diametro, *medidas)
    if st.session_state.get("avaliacao_atual") != assinatura:
        st.session_state.pop("avaliacao_atual", None)

    if st.button(t("Avaliar ligação"), key="avaliar_ligacao", type="primary", use_container_width=True):
        if any(m is None or m <= 0 for m in medidas):
            st.warning(t("Preencha as quatro medições com valores maiores que zero para avaliar."))
        else:
            st.session_state["avaliacao_atual"] = assinatura

    if st.session_state.get("avaliacao_atual") == assinatura:
        st.divider()
        st.subheader(t("Resultado da avaliação"))
        st.caption(t("NPS {nps} · Classe {classe} · Estojo {diametro}").format(nps=exibir_nps(nps, idioma_atual), classe=classe, diametro=diametro))
        resultado = avaliar(nps, classe, tipo, *medidas)
        aprovados = [d["aprovado"] for d in resultado["dimensoes"]]
        if resultado["aprovado"]:
            st.success(t("APROVADO NO CRITÉRIO DIMENSIONAL · As quatro medidas atendem aos mínimos cadastrados."))
        else:
            st.error(t("REPROVADO NO CRITÉRIO DIMENSIONAL · Há medidas abaixo dos mínimos cadastrados."))

        st.markdown("#### " + t("Conferência das dimensões"))
        for inicio in (0, 2):
            colunas = st.columns(2)
            for i in range(inicio, inicio + 2):
                with colunas[i - inicio], st.container(border=True):
                    st.markdown(f"**{labels[i]}**")
                    if aprovados[i]:
                        st.success(t("Atende ao mínimo"))
                    else:
                        st.error(t("Abaixo do mínimo"))
                    st.markdown(
                        f'{t("Medido")}: **{numero(medidas[i])} mm**  \n'
                        f'{t("Nominal")}: **{numero(nominais[i])} mm**  \n'
                        f'{t("Mínimo aceitável")}: **{numero(limites[i])} mm**'
                    )
                    diferenca = medidas[i] - limites[i]
                    sinal = "+" if diferenca >= 0 else ""
                    st.caption(f'{t("Diferença")}: {sinal}{numero(diferenca)} mm')
    else:
        st.caption(t("Preencha ou revise os dados e toque em Avaliar ligação para obter o resultado atualizado."))

    with st.expander(t("Como interpretar esta avaliação")):
        st.write(t("A aprovação dimensional exige que as quatro medidas sejam iguais ou superiores aos limites cadastrados. A porca deve atender tanto à altura H quanto à largura F."))
        st.write(t("O valor nominal é a referência dimensional cadastrada. A aprovação usa o mínimo admissível; uma medida abaixo do nominal ainda pode atender ao critério."))
        st.caption(t("Os valores de referência são os cadastrados nas tabelas deste aplicativo."))
