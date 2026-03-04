import io
import textwrap
import unicodedata
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# =================================================================
# 1. CONFIGURAÇÕES E NORMALIZAÇÃO
# =================================================================
st.set_page_config(page_title="Painel Diagnóstico - Máxima Leitura", layout="wide")

def _strip_accents(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch))

# =================================================================
# 2. CARREGAMENTO E TRATAMENTO DE DADOS
# =================================================================
@st.cache_data(show_spinner="Sincronizando dados...")
def load_and_merge_full(file_bytes):
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    df_lan = pd.read_excel(xls, sheet_name="Lancamentos")
    
    if "Turma" in df_lan.columns:
        df_lan["Turma"] = df_lan["Turma"].astype(str).str.upper().str.strip()

    try:
        df_hab = pd.read_excel(xls, sheet_name="Habilidades")
        df_hab = df_hab[['HAB_ID', 'Ano/Série', 'Disciplina', 'Habilidade']].drop_duplicates(subset=['HAB_ID'])
        df = pd.merge(df_lan, df_hab, on="HAB_ID", how="left", suffixes=('', '_ref'))
        for col in ['Ano/Série', 'Disciplina', 'Habilidade']:
            if f"{col}_ref" in df.columns:
                df[col] = df[col].fillna(df[f"{col}_ref"])
    except:
        df = df_lan

    for c in ["Total de alunos", "SIM", "PARCIAL", "NÃO"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    return df

# =================================================================
# 3. GERAÇÃO DE PDF (MÁXIMO APROVEITAMENTO)
# =================================================================
def build_pdf_final_ultra(fig, filtros):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4))
    width, height = landscape(A4) 
    
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.8*cm, height - 1.2*cm, "RELATÓRIO DIAGNÓSTICO POR HABILIDADE")
    
    c.setFont("Helvetica", 11)
    info = f"Série: {filtros['Série']} | Disciplina: {filtros['Disciplina']} | Turmas: {filtros['Turmas']}"
    c.drawString(0.8*cm, height - 1.9*cm, info)
    
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=300) 
    img_buf.seek(0)
    
    # Desenho que respeita a proporção para não esticar as letras
    c.drawImage(ImageReader(img_buf), 0.5*cm, 0.5*cm, width=width-1.0*cm, height=height-3.5*cm, preserveAspectRatio=True)
    
    c.showPage()
    c.save()
    return buf.getvalue()

# =================================================================
# 4. INTERFACE E DASHBOARD
# =================================================================
st.title("📊 Painel Diagnóstico")

uploaded = st.file_uploader("Upload da Planilha FIX2000", type=["xlsx"])

if uploaded:
    df_raw = load_and_merge_full(uploaded.read())
    
    with st.sidebar:
        st.header("🎯 Filtros")
        series = sorted([str(x) for x in df_raw["Ano/Série"].dropna().unique()])
        ano_sel = st.selectbox("Ano/Série", ["Todos"] + series)
        discs = sorted([str(x) for x in df_raw["Disciplina"].dropna().unique()])
        disc_sel = st.selectbox("Disciplina", ["Todas"] + discs)
        turmas = sorted([str(x) for x in df_raw["Turma"].dropna().unique()])
        turma_sel = st.multiselect("Filtrar Turmas", turmas, default=turmas)
        
        st.markdown("---")
        st.info(f"🆘 Suporte Técnico: (18) 98121-1497 (Jean)")

    df_f = df_raw[df_raw["Turma"].isin(turma_sel)]
    if ano_sel != "Todos": df_f = df_f[df_f["Ano/Série"] == ano_sel]
    if disc_sel != "Todas": df_f = df_f[df_f["Disciplina"] == disc_sel]

    def wrap_label(id_hab, texto):
        return "\n".join(textwrap.wrap(f"{id_hab} - {texto}", width=50))

    df_agg = df_f.groupby(["HAB_ID", "Habilidade"]).agg({
        "SIM": "sum", "PARCIAL": "sum", "NÃO": "sum", "Total de alunos": "sum"
    }).reset_index()

    df_agg["Label"] = df_agg.apply(lambda x: wrap_label(x["HAB_ID"], x["Habilidade"]), axis=1)

    den = df_agg["Total de alunos"].replace(0, 1)
    df_agg["p_sim"] = (df_agg["SIM"] / den) * 100
    df_agg["p_par"] = (df_agg["PARCIAL"] / den) * 100
    df_agg["p_nao"] = (df_agg["NÃO"] / den) * 100
    df_agg = df_agg.sort_values("p_sim")

    # --- GRÁFICO CORRIGIDO ---
    altura_fig = max(8, len(df_agg) * 1.2)
    fig, ax = plt.subplots(figsize=(20, altura_fig))
    
    ax.barh(df_agg["Label"], df_agg["p_sim"], color="#2ecc71", label="SIM")
    ax.barh(df_agg["Label"], df_agg["p_par"], left=df_agg["p_sim"], color="#f1c40f", label="PARCIAL")
    ax.barh(df_agg["Label"], df_agg["p_nao"], left=df_agg["p_sim"]+df_agg["p_par"], color="#e74c3c", label="NÃO")

    # Fonte 14 e alinhamento total à esquerda
    ax.set_yticklabels(df_agg["Label"], fontweight='bold', fontsize=14, ha='right')

    # Margens que garantem o texto na esquerda e barras na direita
    plt.subplots_adjust(left=0.42, right=0.98, top=0.98, bottom=0.08) 

    for i in range(len(df_agg)):
        s, p, n = int(df_agg["SIM"].iloc[i]), int(df_agg["PARCIAL"].iloc[i]), int(df_agg["NÃO"].iloc[i])
        ps, pp, pn = df_agg["p_sim"].iloc[i], df_agg["p_par"].iloc[i], df_agg["p_nao"].iloc[i]
        
        if ps > 5:
            ax.text(ps/2, i, f"{s}\n({ps:.0f}%)", va='center', ha='center', color='white', fontweight='bold', fontsize=11)
        if pp > 5:
            ax.text(ps + pp/2, i, f"{p}\n({pp:.0f}%)", va='center', ha='center', color='black', fontweight='bold', fontsize=11)
        if pn > 5:
            ax.text(ps + pp + pn/2, i, f"{n}\n({pn:.0f}%)", va='center', ha='center', color='white', fontweight='bold', fontsize=11)

    ax.set_xlim(0, 100)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=12, frameon=False)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    st.pyplot(fig, use_container_width=True)

    st.divider()
    if st.button("🖨️ Gerar PDF Final Maximizado"):
        filtros_pdf = {"Série": ano_sel, "Disciplina": disc_sel, "Turmas": ", ".join(turma_sel)}
        pdf_bytes = build_pdf_final_ultra(fig, filtros_pdf)
        st.download_button("Baixar Relatório PDF", pdf_bytes, f"Diagnostica_Final_{ano_sel}.pdf")

else:
    st.info("Aguardando planilha...")
