import streamlit as st
import json

# =========================
# CARREGAR DADOS
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
# SOLVER
# =========================
def avaliar(nps, classe, tipo, diametro, mat_f, mat_e, fluido, hist, perda,
            tf_med, d_med, h_med, f_med):

    # buscar flange
    flange = next((f for f in flanges if f["nps_pol"] == nps and f["classe"] == classe and f["tipo"] == tipo), None)

    # buscar estojo
    estojo = next((e for e in estojos if e["diametro_nominal"] == diametro), None)

    if not flange or not estojo:
        return "Erro nos dados"

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


# =========================
# INTERFACE
# =========================
st.title("RTI + Preservação")

nps = st.selectbox("NPS", list(set([f["nps_pol"] for f in flanges])))
classe = st.selectbox("Classe", list(set([f["classe"] for f in flanges])))
tipo = st.selectbox("Tipo", list(set([f["tipo"] for f in flanges])))
estojo = st.selectbox("Estojo", list(set([e["diametro_nominal"] for e in estojos])))

mat_f = st.selectbox("Material Flange", ["Aço Carbono", "Aço Inox / Duplex", "Cu/Ni"])
mat_e = st.selectbox("Material Estojo", ["Aço Carbono"])
fluido = st.selectbox("Fluido", ["APSO", "BP"])
hist = st.selectbox("Histórico", list(set([r["historico_do_sistema"] for r in rti])))
perda = st.selectbox("Perda", ["Sim", "Não"])

tf_med = st.number_input("tf med", value=10.0)
d_med = st.number_input("D med", value=10.0)
h_med = st.number_input("H med", value=10.0)
f_med = st.number_input("F med", value=10.0)

if st.button("Avaliar"):
    resultado = avaliar(nps, classe, tipo, estojo, mat_f, mat_e, fluido, hist, perda,
                        tf_med, d_med, h_med, f_med)
    st.success(resultado)
