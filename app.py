import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# 1. Configuração da Página
st.set_page_config(page_title="Painel de Avaliação", layout="wide")
st.title("📊 Painel Diagnóstico e Emissão de PDF")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

# 2. Função para o PDF (Cores e layout baseados no seu modelo)
def gerar_pdf(dados, serie, disciplina, turma):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Azul Escuro
    pdf.set_fill_color(31, 73, 125)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, 'RELATÓRIO DIAGNÓSTICO POR HABILIDADE', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 5, f'Série: {serie} | Disciplina: {disciplina} | Turma: {turma}', 0, 1, 'C')
    
    pdf.ln(25)
    pdf.set_text_color(0, 0, 0)
    
    # Tabela de Resultados
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(100, 10, 'Habilidade', 1, 0, 'L', True)
    pdf.cell(30, 10, 'SIM', 1, 0, 'C', True)
    pdf.cell(30, 10, 'PARCIAL', 1, 0, 'C', True)
    pdf.cell(30, 10, 'NÃO', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 8)
    for _, row in dados.iterrows():
        # Trata o texto para caber na linha
        desc = f"{row['HAB_ID']} - {row['Habilidade']}"
        if len(desc) > 70: desc = desc[:67] + "..."
        
        pdf.cell(100, 8, desc.encode('latin-1', 'replace').decode('latin-1'), 1)
        pdf.cell(30, 8, str(row['SIM']), 1, 0, 'C')
        pdf.cell(30, 8, str(row['PARCIAL']), 1, 0, 'C')
        pdf.cell(30, 8, str(row['NÃO']), 1, 1, 'C')
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# 3. Lógica do Sistema
if uploaded_file:
    try:
        # Lê a aba de Lançamentos sem pular nada
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        df.columns = [str(c).strip() for c in df.columns]

        # Filtros Laterais
        st.sidebar.header("Filtros")
        sel_disc = st.sidebar.selectbox("Disciplina", sorted(df['Disciplina'].dropna().unique()))
        
        df_disc = df[df['Disciplina'] == sel_disc]
        sel_serie = st.sidebar.selectbox("Série", sorted(df_disc['Ano/Série'].dropna().unique()))
        
        df_serie = df_disc[df_disc['Ano/Série'] == sel_serie]
        sel_turma = st.sidebar.selectbox("Turma", sorted(df_serie['Turma'].dropna().unique()))

        # Dados Filtrados
        final = df_serie[df_serie['Turma'] == sel_turma]

        if not final.empty:
            st.subheader(f"✅ Visualização: {sel_disc} - {sel_serie} (Turma {sel_turma})")

            # --- GRÁFICOS NO SITE (NATIVOS) ---
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### Desempenho por Questão")
                # Gráfico de barras horizontal nativo (Questão vs Resultados)
                chart_data = final.set_index('Questão/Item')[['SIM', 'PARCIAL', 'NÃO']]
                st.bar_chart(chart_data)

            with col2:
                st.write("### Total da Turma")
                # Gráfico de pizza simulado por barras para evitar dependência de Plotly
                totais = pd.DataFrame({
                    'Avaliação': ['SIM', 'PARCIAL', 'NÃO'],
                    'Total': [final['SIM'].sum(), final['PARCIAL'].sum(), final['NÃO'].sum()]
                }).set_index('Avaliação')
                st.bar_chart(totais)

            # Tabela de Conferência
            st.write("### Tabela de Habilidades")
            st.dataframe(final[['Questão/Item', 'Habilidade', 'SIM', 'PARCIAL', 'NÃO']], use_container_width=True)

            # --- BOTÃO DE PDF ---
            st.divider()
            pdf_bytes = gerar_pdf(final, sel_serie, sel_disc, sel_turma)
            st.download_button(
                label="📥 GERAR RELATÓRIO PDF PARA COORDENAÇÃO",
                data=pdf_bytes,
                file_name=f"Relatorio_{sel_serie}_{sel_turma}.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("Selecione os filtros acima para carregar os dados.")

    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
