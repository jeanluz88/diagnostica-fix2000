import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# 1. Configurações iniciais
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.markdown("<style>.big-font { font-size:14pt !important; }</style>", unsafe_allow_html=True)

st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Upload da Planilha Modelo_Diagnostica_Por_Turma", type=["xlsx"])

if uploaded_file:
    try:
        # Lê a planilha
        df = pd.read_excel(uploaded_file)
        
        # --- LIMPEZA AUTOMÁTICA DE COLUNAS ---
        # Remove espaços e padroniza para evitar erros de acentuação
        df.columns = [str(c).strip().replace('Série', 'Serie').replace('SÉRIE', 'Serie') for c in df.columns]

        # Verifica colunas essenciais
        colunas_obrigatorias = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        existentes = [c for c in colunas_obrigatorias if c in df.columns]
        
        if len(existentes) < len(colunas_obrigatorias):
            faltando = list(set(colunas_obrigatorias) - set(existentes))
            st.error(f"⚠️ Erro: Não encontramos as colunas: {', '.join(faltando)}")
            st.info("Certifique-se de que os nomes na primeira linha da planilha estão corretos.")
        else:
            # Limpa os dados internos (remove espaços em branco)
            for col in existentes:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS ÚNICOS (Acaba com a duplicidade de Língua Portuguesa) ---
            st.sidebar.header("Filtros")
            
            lista_disc = sorted(df['Disciplina'].unique())
            disc_sel = st.sidebar.selectbox("Selecione a Disciplina", lista_disc)

            # Filtra séries com base na disciplina
            df_aux = df[df['Disciplina'] == disc_sel]
            lista_ser = sorted(df_aux['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Selecione a Série", lista_ser)

            # Filtra turmas com base na série
            df_aux = df_aux[df_aux['Serie'] == serie_sel]
            lista_tur = sorted(df_aux['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Selecione a Turma", lista_tur)

            # Dados finais para exibição
            df_final = df_aux[df_aux['Turma'] == turma_sel]

            # --- EXIBIÇÃO ---
            c1, c2 = st.columns([1.5, 1])

            with c1:
                st.subheader("Habilidades")
                for _, row in df_final.iterrows():
                    # Usa get para não travar caso a coluna de descrição mude de nome
                    desc = row.get('Habilidade_Descricao', 'Descrição não disponível')
                    cod = row.get('Habilidade_Codigo', '-')
                    st.markdown(f'<p class="big-font"><b>{cod}:</b> {desc}</p>', unsafe_allow_html=True)

            with c2:
                st.subheader("Desempenho")
                if not df_final.empty:
                    fig, ax = plt.subplots()
                    contagem = df_final['Resultado'].value_counts()
                    ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'])
                    st.pyplot(fig)
                    
                    if st.button("📄 Baixar Relatório PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(200,
