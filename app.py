import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# Configurações de interface
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.markdown("<style>.big-font { font-size:14pt !important; }</style>", unsafe_allow_html=True)

st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Upload da Planilha Modelo_Diagnostica_Por_Turma", type=["xlsx"])

if uploaded_file:
    try:
        # Lê a planilha e remove espaços dos nomes das colunas
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip() for c in df.columns]

        # MAPEAMENTO INTELIGENTE: Traduz nomes com ou sem acento
        mapeamento = {
            'Série': 'Serie', 'SERIE': 'Serie', 'serie': 'Serie',
            'Língua Portuguesa': 'Lingua Portuguesa',
            'Resultado': 'Resultado', 'RESULTADO': 'Resultado'
        }
        df.rename(columns=mapeamento, inplace=True)

        # Verifica se as colunas básicas existem
        colunas_obrigatorias = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        faltando = [c for c in colunas_obrigatorias if c not in df.columns]

        if faltando:
            st.error(f"⚠️ Erro na Planilha: Faltam as colunas: {', '.join(faltando)}")
            st.info("Dica: Verifique se os nomes das colunas estão na primeira linha.")
        else:
            # Limpa os dados para remover duplicados por espaços extras
            for c in colunas_obrigatorias:
                df[c] = df[c].astype(str).str.strip()

            # FILTROS ÚNICOS (Sem duplicar Língua Portuguesa)
            st.sidebar.header("Configurações")
            disciplinas = sorted(df['Disciplina'].unique())
            disc_sel = st.sidebar.selectbox("Disciplina", disciplinas)

            series = sorted(df[df['Disciplina'] == disc_sel]['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Série", series)

            turmas = sorted(df[(df['Disciplina'] == disc_sel) & (df['Serie'] == serie_sel)]['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Turma", turmas)

            # Filtragem final
            final_df = df[(df['Disciplina'] == disc_sel) & (df['Serie'] == serie_sel) & (df['Turma'] == turma_sel)]

            # EXIBIÇÃO LADO A LADO
            c1, c2 = st.columns([1.5, 1])

            with c1:
                st.subheader("Habilidades Analisadas")
                for _, row in final_df.iterrows():
                    desc = row.get('Habilidade_Descricao', 'Descrição não encontrada')
                    cod = row.get('Habilidade_Codigo', 'Cod')
                    st.markdown(f'<p class="big-font"><b>{cod}:</b> {desc}</p>', unsafe_allow_html=True)

            with c2:
                st.subheader("Gráfico de Desempenho")
                if not final_df.empty:
                    fig, ax = plt.subplots()
                    contagem = final_df['Resultado'].value_counts()
                    ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#4CAF50', '#FFC107', '#F44336'])
                    st.pyplot(fig)

                    if st.button("📄 Gerar PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 16)
                        pdf.cell(200, 10, f"Relatorio: {disc_sel} - {serie_sel}", ln=True, align='C')
                        st.download_button("📥 Baixar PDF", data=pdf.output(dest='S').encode('latin-1', 'replace'), file_name="Relatorio.pdf")
                else:
                    st.warning("Nenhum dado encontrado para esta seleção.")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
else:
    st.info("Aguardando o upload da planilha Modelo_Diagnostica_Por_Turma...")
