import tkinter as tk
from tkinter import ttk, messagebox
import json


# =========================
# FUNÇÃO AUXILIAR
# =========================
def to_float(x):
    return float(str(x).replace(",", "."))


# =========================
# CARREGAR BASES
# =========================
with open("AvFlanges.json", "r", encoding="utf-8") as f:
    flanges = json.load(f)

with open("AvEstojosPorcas.json", "r", encoding="utf-8") as f:
    estojos = json.load(f)

with open("ClasseRTI.json", "r", encoding="utf-8") as f:
    rti = json.load(f)


# =========================
# FUNÇÕES SOLVER
# =========================
def buscar_flange(nps, classe, tipo):
    for f in flanges:
        if f["nps_pol"] == nps and f["classe"] == classe and f["tipo"] == tipo:
            return {
                "tf_min": to_float(f["tfmin_mm"])
            }
    return None


def buscar_estojo(diametro):
    for e in estojos:
        if e["diametro_nominal"] == diametro:
            return e
    return None


def selecionar_d_min(estojo, tipo):
    if "B16.47" in tipo:
        return estojo["d_min_b16_47"]
    return estojo["d_min_b16_5"]


def buscar_rti(mat_f, mat_e, fluido, hist, perda, aprovado):
    for linha in rti:
        if (
            linha["material_do_flange"] == mat_f
            and linha["material_do_estojo"] == mat_e
            and linha["fluido"] == fluido
            and linha["historico_do_sistema"] == hist
            and linha["possui_perda_de_massa"] == perda
            and linha["aprovado_no_criterio"] == aprovado
        ):
            return linha["classificacao_rti"], linha["preservacao"]
    return "Não encontrado", ""


# =========================
# AÇÃO DO BOTÃO
# =========================
def rodar():

    try:
        flange = buscar_flange(cb_nps.get(), cb_classe.get(), cb_tipo.get())
        estojo = buscar_estojo(cb_estojo.get())

        if not flange:
            messagebox.showerror("Erro", "Flange não encontrado")
            return

        if not estojo:
            messagebox.showerror("Erro", "Estojo não encontrado")
            return

        tf_med = to_float(ent_tf.get())
        d_med = to_float(ent_d.get())
        h_med = to_float(ent_h.get())
        f_med = to_float(ent_f.get())

        d_min = selecionar_d_min(estojo, cb_tipo.get())

        flange_ok = tf_med >= flange["tf_min"]
        estojo_ok = d_med >= d_min
        porca_ok = (h_med >= estojo["H_min"] and f_med >= estojo["F_min"])

        aprovado = "Sim" if (flange_ok and estojo_ok and porca_ok) else "Não"

        rti_val, pres = buscar_rti(
            cb_mat_flange.get(),
            cb_mat_estojo.get(),
            cb_fluido.get(),
            cb_hist.get(),
            cb_perda.get(),
            aprovado
        )

        resultado.set(f"RTI: {rti_val}\nPreservação: {pres}")

    except Exception as e:
        messagebox.showerror("Erro", str(e))


# =========================
# INTERFACE
# =========================
root = tk.Tk()
root.title("RTI + Preservação")
root.geometry("600x500")

# Forçar aparecer na frente
root.lift()
root.attributes("-topmost", True)
root.after(100, lambda: root.attributes("-topmost", False))

# =========================
# DROPDOWNS
# =========================
cb_nps = ttk.Combobox(root, values=list(set([f["nps_pol"] for f in flanges])))
cb_classe = ttk.Combobox(root, values=list(set([f["classe"] for f in flanges])))
cb_tipo = ttk.Combobox(root, values=list(set([f["tipo"] for f in flanges])))
cb_estojo = ttk.Combobox(root, values=list(set([e["diametro_nominal"] for e in estojos])))

cb_mat_flange = ttk.Combobox(root, values=["Aço Carbono", "Aço Inox / Duplex", "Cu/Ni"])
cb_mat_estojo = ttk.Combobox(root, values=["Aço Carbono"])
cb_fluido = ttk.Combobox(root, values=["APSO", "BP"])
cb_hist = ttk.Combobox(root, values=list(set([r["historico_do_sistema"] for r in rti])))
cb_perda = ttk.Combobox(root, values=["Sim", "Não"])

# =========================
# ENTRADAS
# =========================
ent_tf = tk.Entry(root)
ent_d = tk.Entry(root)
ent_h = tk.Entry(root)
ent_f = tk.Entry(root)

# =========================
# LAYOUT
# =========================
labels = [
    ("NPS", cb_nps),
    ("Classe", cb_classe),
    ("Tipo", cb_tipo),
    ("Estojo", cb_estojo),
    ("Material Flange", cb_mat_flange),
    ("Material Estojo", cb_mat_estojo),
    ("Fluido", cb_fluido),
    ("Histórico", cb_hist),
    ("Perda", cb_perda),
    ("tf med", ent_tf),
    ("D med", ent_d),
    ("H med", ent_h),
    ("F med", ent_f),
]

for i, (txt, widget) in enumerate(labels):
    tk.Label(root, text=txt).grid(row=i, column=0, sticky="w", padx=5)
    widget.grid(row=i, column=1, padx=5, pady=2)

# =========================
# BOTÃO
# =========================
btn = tk.Button(root, text="Avaliar", command=rodar)
btn.grid(row=len(labels), column=0, columnspan=2, pady=10)

# =========================
# RESULTADO
# =========================
resultado = tk.StringVar()
lbl_resultado = tk.Label(root, textvariable=resultado, fg="blue")
lbl_resultado.grid(row=len(labels)+1, column=0, columnspan=2)

# =========================
# EXECUÇÃO
# =========================
root.mainloop()
