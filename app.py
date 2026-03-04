import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Gerador de Relatório PDF", layout="wide")
st.title("📊 Gerador de Relatório Diagnóstico (PDF)")

uploaded_file = st.file_uploader("Carregue a planilha NAVARRO.xlsx", type=["xlsx"])

# Função para criar o PDF no formato do modelo enviado
def gerar_pdf(dados, serie, disciplina, turma):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Azul
    pdf.set_fill_color(31, 73, 125)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'RELATÓRIO DIAGNÓSTICO POR HABILIDADE', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Série: {serie} | Disciplina: {disciplina} | Turma: {turma}', 0, 1, 'C')
    
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)
    
    # Tabela de Habilidades
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(110, 10, 'Habilidade', 1)
    pdf.cell(25, 10, 'SIM', 1, 0, 'C')
    pdf.cell(25, 10, 'PARCIAL', 1, 0, 'C')
    pdf.cell(25, 10, 'NÃO', 1, 1, 'C')
    
    pdf.set_font('Arial', '', 9)
    for index, row in dados.iterrows():
        # Trunca o texto da habilidade para não vazar a célula
        texto_hab = str(row['Habilidade'])[:60] + "..." if len(str(row['Habilidade'])) > 60 else str(row['Habilidade'])
        pdf.cell(110, 8, texto_hab, 1)
        pdf.cell(25, 8, str(row['SIM']), 1, 0, 'C')
        pdf.cell(25, 8, str(row['PARCIAL']), 1, 0, 'C')
        pdf.cell(25, 8, str(row['NÃO']), 1, 1, 'C')
        
    return pdf.output(dest='S').encode('latin-1')

if uploaded_file:
    try:
        # Lendo a aba Lancamentos (Sem pular linhas - Linha 0 é o título)
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        df.columns = [str(c).strip() for c in df.columns]

        # Filtros
        st.sidebar.header("Configuração do Relatório")
        sel_disc = st.sidebar.selectbox("Disciplina", sorted(df['Disciplina'].unique()))
        
        df_aux = df[df['Disciplina'] == sel_disc]
        sel_serie = st.sidebar.selectbox("Série", sorted(df_aux['Ano/Série'].unique()))
        
        sel_turma = st.sidebar.selectbox("Turma", sorted(df_aux[df_aux['Ano/Série'] == sel_serie]['Turma'].unique()))

        final = df_aux[(df_aux['Ano/Série'] == sel_serie) & (df_aux['Turma'] == sel_turma)]

        if not final.empty:
            st.success(f"Dados prontos para o PDF: {sel_serie} - {sel_turma}")
            st.dataframe(final[['Questão/Item', 'Habilidade', 'SIM', 'PARCIAL', 'NÃO']], use_container_width=True)

            # Botão de Gerar PDF
            pdf_bytes = gerar_pdf(final, sel_serie, sel_disc, sel_turma)
            
            st.download_button(
                label="📥 Baixar Relatório em PDF (IGUAL AO MODELO)",
                data=pdf_bytes,
                file_name=f"Relatorio_{sel_serie}_{sel_turma}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Nenhum dado encontrado para os filtros.")

    except Exception as e:
        st.error(f"Erro: {e}")
