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
        # Lê a planilha
        df = pd.read_excel(uploaded_file)
        
        # --- NORMALIZAÇÃO DE COLUNAS (Evita o erro KeyError: 'Serie') ---
        # Remove espaços e padroniza 'Série' com ou sem acento
        df.columns = [str(c).strip().replace('Série', 'Serie').replace('SÉRIE', 'Serie') for c in df.columns]

        # Verifica se as 4 colunas vitais existem
        col_req = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        existentes = [c for c in col_req if c in df.columns]

        if len(existentes) < len(col_req):
            faltando = list(set(col_req) - set(existentes))
            st.error(f"⚠️ Erro na Planilha: Faltam as colunas: {', '.join(faltando)}")
        else:
            # Limpa dados internos para evitar duplicados como 'Língua Portuguesa '
            for col in col_req:
                df[col] = df[col].astype(str).str.strip()

            # --- SISTEMA DE FILTROS ÚNICOS ---
            st.sidebar.header("Filtros")
            lista_disc = sorted(df['Disciplina'].unique())
            disc_sel = st.sidebar.selectbox("Disciplina", lista_disc)

            df_aux = df[df['Disciplina'] == disc_sel]
            lista_ser = sorted(df_aux['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Série", lista_ser)

            lista_tur = sorted(df_aux[df_aux['Serie'] == serie_sel]['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Turma", lista_tur)

            # Filtro Final
            df_final = df_aux[(df_aux['Serie'] == serie_sel) & (df_aux['Turma'] == turma_sel)]

            # --- EXIBIÇÃO EM COLUNAS ---
            c1, c2 = st.columns([1.5, 1])

            with c1:
                st.subheader("Habilidades")
                if not df_final.empty:
                    for _, row in df_final.iterrows():
                        cod = row.get('Habilidade_Codigo', '-')
                        desc = row.get('Habilidade_Descricao', 'Descrição ausente')
                        st.markdown(f'<p class="big-font"><b>{cod}:</b> {desc}</p>', unsafe_allow_html=True)
                else:
                    st.write("Selecione os dados para exibir as habilidades.")

            with c2:
                st.subheader("Desempenho")
                if not df_final.empty:
                    # Gráfico de Pizza
                    fig, ax = plt.subplots()
                    contagem = df_final['Resultado'].value_counts()
                    ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'])
                    st.pyplot(fig)
                    
                    # --- GERAÇÃO DE PDF (Sintaxe e Indentação Corrigidas) ---
                    if st.button("📄 Gerar Relatório PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(200, 10, txt=f"Relatorio: {disc_sel} - {serie_sel}", ln=True, align='C')
                        
                        pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
                        st.download_button(label="📥 Baixar PDF", data=pdf_out, file_name="Relatorio.pdf", mime="application/pdf")
                else:
                    st.warning("Aguardando seleção de Turma.")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
else:
    st.info("Aguardando upload da planilha...")
