import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# Configuração da página e estilo
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.markdown("<style>.big-font { font-size:14pt !important; }</style>", unsafe_allow_html=True)

st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Upload da Planilha Modelo_Diagnostica_Por_Turma", type=["xlsx"])

if uploaded_file:
    try:
        # Lendo a planilha (ajuste o nome da aba se necessário)
        df = pd.read_excel(uploaded_file)
        
        # Padronização: remove espaços e garante que nomes de colunas existam
        df.columns = [str(c).strip() for c in df.columns]
        
        # Verificação de segurança para as colunas principais
        colunas_necessarias = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        colunas_faltando = [c for c in colunas_necessarias if c not in df.columns]

        if colunas_faltando:
            st.error(f"Atenção: A planilha precisa ter as colunas: {', '.join(colunas_faltando)}")
        else:
            # Limpeza de dados para evitar duplicados como "Lingua Portuguesa"
            for col in ['Disciplina', 'Serie', 'Turma']:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS ÚNICOS (Correção da Duplicidade) ---
            st.sidebar.header("Filtros")
            disciplinas = sorted(df['Disciplina'].unique())
            disciplina_sel = st.sidebar.selectbox("Disciplina", disciplinas)

            series = sorted(df[df['Disciplina'] == disciplina_sel]['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Série", series)

            turmas = sorted(df[(df['Disciplina'] == disciplina_sel) & (df['Serie'] == serie_sel)]['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Turma", turmas)

            # Filtragem final
            dados_filtrados = df[(df['Disciplina'] == disciplina_sel) & 
                                 (df['Serie'] == serie_sel) & 
                                 (df['Turma'] == turma_sel)]

            # --- LAYOUT ---
            col1, col2 = st.columns([1.5, 1])

            with col1:
                st.subheader("Habilidades")
                if 'Habilidade_Descricao' in dados_filtrados.columns:
                    for i, row in dados_filtrados.iterrows():
                        codigo = row.get('Habilidade_Codigo', 'Cod')
                        st.markdown(f'<p class="big-font"><b>{codigo}:</b> {row["Habilidade_Descricao"]}</p>', unsafe_allow_html=True)
                else:
                    st.warning("Coluna 'Habilidade_Descricao' não encontrada.")

            with col2:
                st.subheader("Desempenho")
                if not dados_filtrados.empty:
                    fig, ax = plt.subplots()
                    contagem = dados_filtrados['Resultado'].value_counts()
                    ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#4CAF50', '#FFC107', '#F44336'])
                    st.pyplot(fig)

                    # --- BOTÃO PDF ---
                    if st.button("Gerar PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 16)
                        pdf.cell(200, 10, f"Relatorio - {disciplina_sel}", ln=True, align='C')
                        pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
                        st.download_button("📥 Baixar PDF", data=pdf_output, file_name="Relatorio.pdf")
                else:
                    st.write("Sem dados para esta seleção.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("Aguardando a planilha Modelo_Diagnostica_Por_Turma...")
