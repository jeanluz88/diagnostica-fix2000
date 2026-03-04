import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# Configurações iniciais
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.markdown("<style>.big-font { font-size:14pt !important; }</style>", unsafe_allow_html=True)

st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Upload da Planilha Modelo_Diagnostica_Por_Turma", type=["xlsx"])

if uploaded_file:
    try:
        # Lê a planilha e limpa os nomes das colunas (remove espaços e acentos comuns)
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().replace('Série', 'Serie').replace('SÉRIE', 'Serie') for c in df.columns]

        # Verifica se as colunas essenciais existem após a limpeza
        colunas_necessarias = ['Disciplina', 'Serie', 'Turma', 'Resultado']
        faltando = [c for c in colunas_necessarias if c not in df.columns]

        if faltando:
            st.error(f"⚠️ Erro na Planilha: Faltam as colunas: {', '.join(faltando)}")
            st.info("Dica: Verifique se os nomes estão na primeira linha da planilha.")
        else:
            # Limpa os dados das células para evitar duplicados
            for col in colunas_necessarias:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS LATERAIS ---
            st.sidebar.header("Filtros")
            lista_disc = sorted(df['Disciplina'].unique())
            disc_sel = st.sidebar.selectbox("Disciplina", lista_disc)

            lista_ser = sorted(df[df['Disciplina'] == disc_sel]['Serie'].unique())
            serie_sel = st.sidebar.selectbox("Série", lista_ser)

            lista_tur = sorted(df[(df['Disciplina'] == disc_sel) & (df['Serie'] == serie_sel)]['Turma'].unique())
            turma_sel = st.sidebar.selectbox("Turma", lista_tur)

            # Filtragem final
            df_final = df[(df['Disciplina'] == disc_sel) & (df['Serie'] == serie_sel) & (df['Turma'] == turma_sel)]

            # --- EXIBIÇÃO ---
            col1, col2 = st.columns([1.5, 1])

            with col1:
                st.subheader("Habilidades")
                for _, row in df_final.iterrows():
                    cod = row.get('Habilidade_Codigo', '-')
                    desc = row.get('Habilidade_Descricao', 'Descrição não encontrada')
                    st.markdown(f'<p class="big-font"><b>{cod}:</b> {desc}</p>', unsafe_allow_html=True)

            with col2:
                st.subheader("Desempenho")
                if not df_final.empty:
                    fig, ax = plt.subplots()
                    contagem = df_final['Resultado'].value_counts()
                    ax.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'])
                    st.pyplot(fig)
                    
                    # CORREÇÃO DO PDF (Parêntese fechado corretamente)
                    if st.button("📄 Gerar Relatório PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", 'B', 14)
                        pdf.cell(200, 10, txt=f"Relatorio: {disc_sel} - {serie_sel}", ln=True, align='C')
                        
                        pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
                        st.download_button(label="📥 Baixar PDF", data=pdf_output, file_name="Relatorio.pdf", mime="application/pdf")
                else:
                    st.warning("Selecione os filtros acima.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("Aguardando o upload da planilha Modelo_Diagnostica_Por_Turma...")
