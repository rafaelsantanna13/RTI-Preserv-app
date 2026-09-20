"""Interface compartilhada pelas duas entradas do Streamlit."""
from html import escape

import streamlit as st

from avaliacao import avaliar, flanges, rti, to_float
from estojos import CORRELACAO, consultar_estojo, norma_do_tipo


def numero(valor):
    return f"{valor:.2f}".replace(".", ",")


def ordem_nps(valor):
    return to_float(valor.split()[0])


def selecionar(label, opcoes, key, **kwargs):
    # Evita manter uma classe/NPS inválida após a troca do tipo de flange.
    if st.session_state.get(key) not in opcoes:
        st.session_state[key] = opcoes[0]
    return st.selectbox(label, opcoes, key=key, **kwargs)


def main():
    st.set_page_config(page_title="RTI + Preservação", page_icon="🔩", layout="centered")
    st.markdown("""
    <style>
    .block-container {max-width: 960px; padding-top: 2rem; padding-bottom: 3rem;}
    .rti-hero {background: #142c43; color: #fff; padding: 28px;
        border-radius: 18px; margin-bottom: 24px; border-top: 5px solid #36c3b2;}
    .rti-hero .eyebrow {font-size: .72rem; font-weight: 700;
        letter-spacing: .12em; color: #8fdfd5; margin-bottom: 10px;}
    .rti-hero h1 {font-size: 2rem; line-height: 1.15; color: #fff;
        padding: 0; margin: 0 0 12px; font-weight: 750;}
    .rti-hero p {color: #d4e1ec; font-size: .95rem; line-height: 1.6; margin: 0;}
    .rti-step {color: #087f8c; font-size: .75rem; font-weight: 700;
        letter-spacing: .08em; margin-bottom: 4px;}
    .rti-result {background: #142c43; color: #fff; padding: 24px;
        border-radius: 14px; margin: 12px 0 20px; overflow-wrap: anywhere;}
    .rti-result small {color: #8fdfd5; font-weight: 700; letter-spacing: .08em;}
    .rti-result h3 {color: #fff; margin: 10px 0; padding: 0; line-height: 1.45;}
    .rti-result p {color: #d4e1ec; margin-bottom: 0;}
    @media (max-width: 640px) {
        .block-container {padding: 1.4rem 1rem 2rem;}
        .rti-hero {padding: 22px 20px;}
        .rti-hero h1 {font-size: 1.7rem;}
    }
    </style>
    <div class="rti-hero">
      <div class="eyebrow">INTEGRIDADE · JUNTAS FLANGEADAS</div>
      <h1>RTI + Preservação</h1>
      <p>Compare as dimensões medidas com os limites cadastrados e consulte
      a classificação RTI e a orientação de preservação.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="rti-step">ETAPA 01</div>', unsafe_allow_html=True)
        st.subheader("Identifique a junta")
        norma = selecionar("Norma / série", ["ASME B16.5", "ASME B16.47 Série A"], "norma")
        tipo = selecionar("Tipo de flange", sorted({f["tipo"] for f in flanges
                          if norma_do_tipo(f["tipo"]) == norma}), "tipo",
                          format_func=lambda valor: valor.removeprefix(norma + " "))
        disponiveis = [f for f in flanges if f["tipo"] == tipo]
        c1, c2 = st.columns(2)
        with c1:
            nps = selecionar("Diâmetro nominal · NPS (pol)",
                             sorted({f["nps_pol"] for f in disponiveis}, key=ordem_nps), "nps")
        with c2:
            classe = selecionar("Classe do flange",
                                sorted({f["classe"] for f in disponiveis if f["nps_pol"] == nps}, key=int), "classe")
        try:
            selecao = consultar_estojo(tipo, nps, classe)
        except ValueError as erro:
            st.session_state.pop("avaliacao_atual", None)
            st.error(str(erro))
            st.stop()
        diametro = selecao["diametro_nominal"]
        st.metric("Diâmetro nominal do estojo · automático", f'{selecao["diametro_pol"]}″')
        st.caption(f'{numero(selecao["diametro_mm"])} mm · Definido por {norma}, NPS {nps} e classe {classe}.')
        st.caption("O diâmetro nominal é automático. O diâmetro medido em campo deve ser informado na etapa 3.")
        with st.expander("Fonte do diâmetro do estojo"):
            fonte = CORRELACAO["fontes"]["sigma"]
            if norma == "ASME B16.5" and ordem_nps(nps) == 22:
                url = CORRELACAO["fontes"]["texas_b16_5_22"]["urls"][classe]
                st.markdown(f"[Texas Flange · Classe {classe}, NPS 22]({url})")
                st.caption("Diâmetro nominal do estojo obtido da furação, conforme a nota (a) da tabela: furo 1/8 pol maior que o estojo.")
            else:
                st.markdown(f'[{fonte["titulo"]}]({fonte["url"]})')
                st.caption(f'Página {fonte["paginas"][norma]} · coluna Stud Diameter.')
            st.caption("Correlação consultada em 20/09/2026. O cadastro de avaliação B16.47 deste aplicativo contempla a Série A.")

    estojo = selecao["criterios"]
    if estojo is None:
        st.session_state.pop("avaliacao_atual", None)
        st.warning(f'O estojo desta combinação é {selecao["diametro_pol"]}″. '
                   "Os limites de avaliação do estojo e da porca ainda não estão cadastrados "
                   "para esse tamanho. O diâmetro nominal está disponível, mas a avaliação RTI fica indisponível até completar esses critérios.")
        st.stop()

    with st.container(border=True):
        st.markdown('<div class="rti-step">ETAPA 02</div>', unsafe_allow_html=True)
        st.subheader("Condições do sistema")
        c1, c2 = st.columns(2)
        with c1:
            mat_f = st.selectbox("Material do flange", ["Aço Carbono", "Aço Inox / Duplex", "Cu/Ni"], key="mat_f")
            fluido = st.selectbox("Fluido", ["APSO", "BP"], key="fluido")
        with c2:
            mat_e = st.selectbox("Material do estojo", ["Aço Carbono"], key="mat_e")
            perda = st.selectbox("Possui perda de massa?", ["Sim", "Não"], key="perda")
        historico = st.selectbox("Histórico de perda de massa",
                                sorted({r["historico_do_sistema"] for r in rti}), key="historico")

    flange = next(f for f in disponiveis if f["nps_pol"] == nps and f["classe"] == classe)
    limites = [to_float(flange["tfmin_mm"]),
               estojo["d_min_b16_47"] if "B16.47" in tipo else estojo["d_min_b16_5"],
               estojo["H_min"], estojo["F_min"]]
    labels = ["Espessura do flange · tf", "Diâmetro do estojo · D",
              "Altura da porca · H", "Largura da porca · F"]
    medidas = []
    with st.container(border=True):
        st.markdown('<div class="rti-step">ETAPA 03</div>', unsafe_allow_html=True)
        st.subheader("Informe as medições")
        st.caption("Todas as medidas em milímetros. Preencha as quatro dimensões medidas em campo.")
        for inicio in (0, 2):
            colunas = st.columns(2)
            for i in range(inicio, inicio + 2):
                with colunas[i - inicio]:
                    medidas.append(st.number_input(
                        labels[i] + " (mm)", min_value=0.0, value=None,
                        step=0.1, format="%.2f", placeholder="Digite a medida",
                        key=f"medida_{i}"))
                    st.caption(f"Mínimo cadastrado: **{numero(limites[i])} mm**")

    assinatura = (tipo, nps, classe, diametro, mat_f, mat_e, fluido, historico, perda, *medidas)
    if st.session_state.get("avaliacao_atual") != assinatura:
        st.session_state.pop("avaliacao_atual", None)

    if st.button("Avaliar junta", type="primary", use_container_width=True):
        if any(m is None or m <= 0 for m in medidas):
            st.warning("Preencha as quatro medições com valores maiores que zero para avaliar.")
        else:
            st.session_state["avaliacao_atual"] = assinatura

    if st.session_state.get("avaliacao_atual") == assinatura:
        st.divider()
        st.subheader("Resultado da avaliação")
        st.caption(f"NPS {nps} · Classe {classe} · Estojo {diametro}")
        aprovados = [m >= limite for m, limite in zip(medidas, limites)]
        if all(aprovados):
            st.success("APROVADO NO CRITÉRIO DIMENSIONAL · As quatro medidas atendem aos mínimos cadastrados.")
        else:
            st.error("REPROVADO NO CRITÉRIO DIMENSIONAL · Há medidas abaixo dos mínimos cadastrados.")

        resultado = avaliar(nps, classe, tipo, mat_f, mat_e, fluido,
                            historico, perda, *medidas)
        if resultado.startswith("RTI: "):
            classificacao, preservacao = resultado[5:].split("\nPreservação: ", 1)
            st.markdown(
                '<div class="rti-result"><small>CLASSIFICAÇÃO RTI</small>'
                f'<h3>{escape(classificacao)}</h3><small>PRESERVAÇÃO</small>'
                f'<p>{escape(preservacao)}</p></div>', unsafe_allow_html=True)
        else:
            st.warning("Classificação RTI não encontrada para esta combinação. "
                       "O resultado dimensional está detalhado abaixo; a orientação de preservação não está disponível.")

        st.markdown("#### Conferência das dimensões")
        for inicio in (0, 2):
            colunas = st.columns(2)
            for i in range(inicio, inicio + 2):
                with colunas[i - inicio], st.container(border=True):
                    st.markdown(f"**{labels[i]}**")
                    if aprovados[i]:
                        st.success("Atende ao mínimo")
                    else:
                        st.error("Abaixo do mínimo")
                    st.markdown(f"Medido: **{numero(medidas[i])} mm**  \n"
                                f"Mínimo: **{numero(limites[i])} mm**")
                    diferenca = medidas[i] - limites[i]
                    st.caption(f"Diferença: {'+' if diferenca >= 0 else ''}{numero(diferenca)} mm")
    else:
        st.caption("Preencha ou revise os dados e toque em Avaliar junta para obter o resultado atualizado.")

    with st.expander("Como interpretar esta avaliação"):
        st.write("A aprovação dimensional exige que as quatro medidas sejam iguais ou superiores "
                 "aos limites cadastrados. A porca deve atender tanto à altura H quanto à largura F.")
        st.write("A classificação RTI cruza esse resultado com os materiais, o fluido, "
                 "o histórico do sistema e a presença de perda de massa.")
        st.caption("Os limites e as orientações são os cadastrados nas tabelas deste aplicativo.")
