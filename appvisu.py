import streamlit as st
import json

# =========================
# CONFIG PAGE
# =========================
st.set_page_config(layout="wide")

# =========================
# LOAD DATA
# =========================
with open("AvFlanges.json") as f:
    flanges = json.load(f)

with open("AvEstojosPorcas.json") as f:
    estojos = json.load(f)

with open("ClasseRTI.json") as f:
    rti = json.load(f)

def to_float(x):
    return float(str(x).replace(",", "."))


# =========================
# SIDEBAR (FILTROS)
# =========================
st.sidebar.title("🔧 Parâmetros")

nps = st.sidebar.selectbox("NPS", sorted(list(set([f["nps_pol"] for f in flanges]))))
classe = st.sidebar.selectbox("Classe", sorted(list(set([f["classe"] for f in flanges]))))
tipo = st.sidebar.selectbox("Tipo", sorted(list(set([f["tipo"] for f in flanges]))))

estojo_sel = st.sidebar.selectbox(
    "Diâmetro Estojo",
    sorted(list(set([e["diametro_nominal"] for e in estojos])))
)

mat_f = st.sidebar.radio("Material do flange", ["Aço Carbono", "Aço Inox / Duplex", "Cu/Ni"])
mat_e = st.sidebar.radio("Material do estojo", ["Aço Carbono"])

fluido = st.sidebar.radio("Fluido", ["APSO", "BP"])
historico = st.sidebar.radio("Histórico", list(set([r["historico_do_sistema"] for r in rti])))
perda = st.sidebar.radio("Perda de massa?", ["Sim", "Não"])


# =========================
# CENTRO - MEDIÇÕES
# =========================
st.title("📊 Matriz de Avaliação")

col1, col2, col3 = st.columns(3)

with col1:
    tf_med = st.number_input("Espessura do Flange (mm)", value=10.0)

with col2:
    d_med = st.number_input("Diâmetro do Estojo (mm)", value=10.0)

with col3:
    f_med = st.number_input("Largura F da Porca (mm)", value=10.0)

h_med = st.number_input("Altura H da Porca (mm)", value=10.0)


# =========================
# SOLVER
# =========================
def avaliar():

    flange = next((f for f in flanges if f["nps_pol"] == nps and f["classe"] == classe and f["tipo"] == tipo), None)
    estojo = next((e for e in estojos if e["diametro_nominal"] == estojo_sel), None)

    if not flange or not estojo:
        return None, None, None

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
        r["historico_do_sistema"] == historico and
        r["possui_perda_de_massa"] == perda and
        r["aprovado_no_criterio"] == aprovado), None)

    if linha:
        return aprovado, linha["classificacao_rti"], linha["preservacao"]

    return aprovado, "N/A", "N/A"


# =========================
# BOTÃO
# =========================
if st.button("✅ Avaliar"):

    status, rti_res, pres = avaliar()

    # =========================
    # RESULTADO VISUAL
    # =========================
    colA, colB = st.columns(2)

    with colA:
        if status == "Sim":
            st.success("✅ APROVADO")
        else:
            st.error("❌ REPROVADO")

    with colB:
        st.metric("RTI", rti_res)

    st.markdown("### 📄 Preservação")
    st.info(pres)
