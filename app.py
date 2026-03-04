import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# 1. Configurações de Interface e Estilo
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.markdown("<style>.big-font { font-size:14pt !important; }</style>", unsafe_allow_html=True)

st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Upload da Planilha Modelo_Diagnostica_Por_Turma", type=["xlsx"])

if uploaded_file:
    try:
        # Lê a planilha
        df = pd.read_excel(uploaded_file)
        
        # --- BLINDAGEM DE COLUNAS ---
        # Remove espaços e trata "Série" com ou sem acento automaticamente
        df.columns = [str(c).strip().replace('Série', 'Serie').replace('SÉRIE', 'Serie') for c in df.columns]

        # Colunas que o sistema precisa encontrar
        col_req = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        faltando = [c for c in col_req if c not in df.columns]

        if faltando:
            st.error(f"⚠️ Erro: Faltam as colunas: {', '.join(faltando)}")
            st.info("Dica: Verifique se os nomes na primeira linha do Excel estão corretos.")
        else:
            # Limpa os dados internos (tira espaços vazios)
            for col in col_req:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS LATERAIS (Sem duplicados) ---
            st.sidebar.header("Filtros de Seleção")
            
            # Filtro de Disciplina (Garante que Lingua Portuguesa apareça uma só vez)
            lista_disc = sorted(df['Disciplina'].unique())
            disc_sel = st.sidebar.selectbox("Selecione a Disciplina", lista_disc)

            # Filtros dinâmicos que dependem da disciplina escolhida
            df_aux = df[df['Disciplina'] == disc_sel]
            lista_ser = sorted(df_aux['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Selecione a Série", lista_ser)

            lista_tur = sorted(df_aux[df_aux['Serie'] == serie_sel]['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Selecione a Turma", lista_tur)

            # Dados finais para exibição
            df_final = df_aux[(df_aux['Serie'] == serie_sel) & (df_aux['Turma'] == turma_sel)]

            # --- EXIBIÇÃO DOS RESULTADOS ---
            col1, col2 = st.columns([1.5, 1])

            with col1:
                st.subheader("Habilidades")
                if not df_final.empty:
                    for _, row in df_final.iterrows():
                        cod = row.get('Habilidade_Codigo', '-')
                        desc = row.get('Habilidade_Descricao', 'Descrição não encontrada')
                        st.markdown(f'<p class="big-font"><b>{cod}:</b> {desc}</p>', unsafe_allow_html=True)
                else:
                    st.write("Nenhuma habilidade encontrada para esta seleção.")

            with col2:
                st.subheader("Desempenho da Turma")
                if not df_final.empty:
                    # Geração do Gráfico
                    fig, ax = plt.subplots()
                    contagem = df_final['Resultado'].value_counts()
                    ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'])
                    st.pyplot(fig)
                    
                    # --- BOTÃO PDF (Sintaxe 100% corrigida) ---
                    if st.button("📄 Gerar Relatório PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(200, 10, txt=f"Relatorio: {disc_sel} - {serie_sel} {turma_sel}", ln=True, align='C')
                        
                        pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
                        st.download_button(label="📥 Baixar PDF", data=pdf_out, file_name="Relatorio.pdf", mime="application/pdf")
                else:
                    st.warning("Selecione os filtros acima para gerar os dados.")

    except Exception as e:
        st.error(f"Erro inesperado no processamento: {e}")
else:
    st.info("Aguardando upload da planilha Modelo_Diagnostica_Por_Turma...")
