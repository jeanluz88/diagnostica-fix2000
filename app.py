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
# 3. GERAÇÃO DE PDF (ESTÉTICA MELHORADA)
# =================================================================
def build_pdf_final_ultra(fig, filtros):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(A4))
    width, height = landscape(A4) 
    
    # Cabeçalho Limpo
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.8*cm, height - 1.2*cm, "RELATÓRIO DIAGNÓSTICO POR HABILIDADE")
    
    c.setFont("Helvetica", 11)
    info = f"Série: {filtros['Série']} | Disciplina: {filtros['Disciplina']} | Turmas: {filtros['Turmas']}"
    c.drawString(0.8*cm, height - 1.9*cm, info)
    
    img_buf = io.BytesIO()
    # bbox_inches='tight' com DPI alto garante nitidez sem esticar artificialmente
    fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=300) 
    img_buf.seek(0)
    
    # preserveAspectRatio=True evita o aspecto "amassado" ou "esticado"
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

    # Quebra de linha inteligente para não "comer" a margem
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

    # --- CONFIGURAÇÃO ESTÉTICA DO GRÁFICO ---
    # Altura baseada no número de itens para manter barras proporcionais
    altura_fig = max(8, len(df
