import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# Configuração da página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")

# Estilo para fonte 14pt
st.markdown("<style>.big-font { font-size:14pt !important; }</style>", unsafe_allow_html=True)

st.title("📊 Painel de Avaliação Diagnóstica")

# Upload do arquivo
uploaded_file = st.file_uploader("Upload da Planilha Modelo_Diagnostica_Por_Turma", type=["xlsx"])

if uploaded_file:
    # Lendo a aba específica
    df = pd.read_excel(uploaded_file, sheet_name="Lancamentos")
    
    # Limpeza de nomes para evitar duplicatas (ex: tirar espaços extras)
    df['Disciplina'] = df['Disciplina'].astype(str).str.strip()
    df['Serie'] = df['Serie'].astype(str).str.strip()
    df['Turma'] = df['Turma'].astype(str).str.strip()

    # --- FILTROS COM VALORES ÚNICOS ---
    st.sidebar.header("Filtros")
    
    # .unique() corrige o erro de aparecer "Língua Portuguesa" duas vezes
    disciplinas = sorted(df['Disciplina'].unique())
    disciplina_sel = st.sidebar.selectbox("Disciplina", disciplinas)

    series = sorted(df[df['Disciplina'] == disciplina_sel]['Serie'].unique())
    serie_sel = st.sidebar.selectbox("Série", series)

    turmas = sorted(df[(df['Disciplina'] == disciplina_sel) & (df['Serie'] == serie_sel)]['Turma'].unique())
    turma_sel = st.sidebar.selectbox("Turma", turmas)

    # Filtragem final dos dados
    dados_filtrados = df[(df['Disciplina'] == disciplina_sel) & 
                         (df['Serie'] == serie_sel) & 
                         (df['Turma'] == turma_sel)]

    # --- LAYOUT LADO A LADO ---
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("Habilidades")
        for i, row in dados_filtrados.iterrows():
            # Exibição com fonte 14pt
            st.markdown(f'<p class="big-font"><b>{row["Habilidade_Codigo"]}:</b> {row["Habilidade_Descricao"]}</p>', unsafe_allow_html=True)

    with col2:
        st.subheader("Desempenho")
        # Gerando o gráfico simples
        fig, ax = plt.subplots()
        contagem = dados_filtrados['Resultado'].value_counts()
        ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#4CAF50', '#FFC107', '#F44336'])
        st.pyplot(fig)

        # --- BOTÃO GERAR PDF ---
        if st.button("Gerar PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, f"Relatório - {disciplina_sel} - {serie_sel} {turma_sel}", ln=True, align='C')
            
            pdf.set_font("Arial", size=12)
            for i, row in dados_filtrados.iterrows():
                texto = f"{row['Habilidade_Codigo']}: {row['Habilidade_Descricao']}"
                pdf.multi_cell(0, 10, texto.encode('latin-1', 'replace').decode('latin-1'))
            
            pdf_output = pdf.output(dest='S').encode('latin-1')
            st.download_button(label="📥 Baixar Relatório PDF", data=pdf_output, file_name="Relatorio_Diagnostica.pdf", mime="application/pdf")

else:
    st.info("Aguardando a planilha Modelo_Diagnostica_Por_Turma...")
