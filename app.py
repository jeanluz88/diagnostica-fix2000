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
        # Lê a planilha e limpa nomes de colunas (remove espaços e acentos)
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().replace('Série', 'Serie').replace('SÉRIE', 'Serie') for c in df.columns]

        # Colunas essenciais
        col_req = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        faltando = [c for c in col_req if c not in df.columns]

        if faltando:
            st.error(f"⚠️ Erro: Faltam as colunas: {', '.join(faltando)}")
        else:
            # Limpeza de dados
            for col in col_req:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS ---
            st.sidebar.header("Filtros")
            lista_disc = sorted(df['Disciplina'].unique())
            disc_sel = st.sidebar.selectbox("Disciplina", lista_disc)

            df_aux = df[df['Disciplina'] == disc_sel]
            lista_ser = sorted(df_aux['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Série", lista_ser)

            lista_tur = sorted(df_aux[df_aux['Serie'] == serie_sel]['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Turma", lista_tur)

            df_final = df_aux[(df_aux['Serie'] == serie_sel) & (df_aux['Turma'] == turma_sel)]

            # --- EXIBIÇÃO ---
            col1, col2 = st.columns([1.5, 1])

            with col1:
                st.subheader("Habilidades")
                for _, row in df_final.iterrows():
                    cod = row.get('Habilidade_Codigo', '-')
                    desc = row.get('Habilidade_Descricao', 'Descrição ausente')
                    st.markdown(f'<p class="big-font"><b>{cod}:</b> {desc}</p>', unsafe_allow_html=True)

            with col2:
                st.subheader("Desempenho")
                if not df_final.empty:
                    fig, ax = plt.subplots()
                    contagem = df_final['Resultado'].value_counts()
                    ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'])
                    st.pyplot(fig)
                    
                    # Correção da Sintaxe do PDF
                    if st.button("📄 Gerar Relatório PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(200, 10, txt=f"Relatorio: {disc_sel} - {serie_sel}", ln=True, align='C')
                        pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
                        st.download_button(label="📥 Baixar PDF", data=pdf_out, file_name="Relatorio.pdf", mime="application/pdf")
                else:
                    st.warning("Selecione os filtros.")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
else:
    st.info("Aguardando upload da planilha...")
