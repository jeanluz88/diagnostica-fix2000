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
        # Lê a planilha e remove espaços dos nomes das colunas
        df = pd.read_excel(uploaded_file)
        
        # --- NORMALIZAÇÃO DE COLUNAS (Blindagem contra erros de acento) ---
        # Converte tudo para string, remove espaços e trata 'Série'
        df.columns = [str(c).strip().replace('Série', 'Serie').replace('SÉRIE', 'Serie') for c in df.columns]

        # Verifica colunas essenciais
        colunas_obrigatorias = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        existentes = [c for c in colunas_obrigatorias if c in df.columns]
        
        if len(existentes) < len(colunas_obrigatorias):
            faltando = list(set(colunas_obrigatorias) - set(existentes))
            st.error(f"⚠️ Erro na Planilha: Faltam as colunas: {', '.join(faltando)}")
            st.info("Dica: Verifique se os nomes na primeira linha do Excel estão como: Disciplina, Série, Turma e Resultado.")
        else:
            # Limpa os dados internos para evitar duplicados
            for col in colunas_obrigatorias:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS ÚNICOS (Sem duplicados) ---
            st.sidebar.header("Filtros")
            lista_disc = sorted(df['Disciplina'].unique())
            disc_sel = st.sidebar.selectbox("Disciplina", lista_disc)

            df_aux = df[df['Disciplina'] == disc_sel]
            lista_ser = sorted(df_aux['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Série", lista_ser)

            lista_tur = sorted(df_aux[df_aux['Serie'] == serie_sel]['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Turma", lista_tur)

            # Dados finais para exibição
            df_final = df_aux[(df_aux['Serie'] == serie_sel) & (df_aux['Turma'] == turma_sel)]

            # --- LAYOUT LADO A LADO ---
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
                    fig, ax = plt.subplots()
                    contagem = df_final['Resultado'].value_counts()
                    ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'])
                    st.pyplot(fig)
                    
                    # --- GERAÇÃO DO PDF (Sintaxe Corrigida) ---
                    if st.button("📄
