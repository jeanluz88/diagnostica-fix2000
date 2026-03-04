import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# 1. Configurações de Interface
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.markdown("<style>.big-font { font-size:14pt !important; }</style>", unsafe_allow_html=True)

st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Upload da Planilha Modelo_Diagnostica_Por_Turma", type=["xlsx"])

if uploaded_file:
    try:
        # Lê a planilha e limpa os nomes das colunas (remove espaços e acentos)
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().replace('Série', 'Serie').replace('SÉRIE', 'Serie') for c in df.columns]

        # Verifica colunas essenciais
        colunas_necessarias = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        faltando = [c for c in colunas_necessarias if c not in df.columns]

        if faltando:
            st.error(f"⚠️ Erro na Planilha: Faltam as colunas: {', '.join(faltando)}")
            st.info("Dica: Verifique se os nomes na primeira linha estão como: Disciplina, Série, Turma e Resultado.")
        else:
            # Limpa os dados internos
            for col in colunas_necessarias:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS ÚNICOS ---
            st.sidebar.header("Filtros")
            lista_disc = sorted(df['Disciplina'].unique())
            disc_sel = st.sidebar.selectbox("Disciplina", lista_disc)

            df_aux = df[df['Disciplina'] == disc_sel]
            lista_ser = sorted(df_aux['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Série", lista_ser)

            lista_tur = sorted(df_aux[df_aux['Serie'] == serie_sel]['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Turma", lista_tur)

            # Filtragem final
            df_final = df_aux[(df_aux['Serie'] == serie_sel) & (df_aux['Turma'] == turma_sel)]

            # --- LAYOUT ---
            col1, col2 = st.columns([1.5, 1])

            with col1:
                st.subheader("Habilidades")
                for _, row in df_final.iterrows():
                    cod = row.get('Habilidade_Codigo', '-')
                    desc = row.get('Habilidade_Descricao', 'Descrição não disponível')
                    st.markdown(f'<p class="big-font"><b>{cod}:</b> {desc}</p>', unsafe_allow_html=True)

            with col2:
                st.subheader("Desempenho")
                if not df_final.empty:
