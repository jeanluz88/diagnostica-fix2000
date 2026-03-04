import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# Configuração da Página
st.set_page_config(page_title="Painel de Avaliação", layout="wide")

# Estilo para o título parecer com o do PDF
st.markdown("<h1 style='text-align: center; color: #1F497D;'>RELATÓRIO DIAGNÓSTICO POR HABILIDADE</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

# --- FUNÇÃO PARA GERAR O PDF IGUAL AO MODELO ---
def gerar_pdf_modelo(dados, serie, disciplina, turma):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Faixa Azul do Topo (Igual ao seu PDF)
    pdf.set_fill_color(31, 73, 125)
    pdf.rect(0, 0, 210, 45, 'F')
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.ln(5)
    pdf.cell(0, 10, 'RELATÓRIO DIAGNÓSTICO POR HABILIDADE', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Série: {serie} | Disciplina: {disciplina} | Turma: {turma}', 0, 1, 'C')
    
    pdf.ln(30)
    pdf.set_text_color(0, 0, 0)
    
    # 2. Tabela de Habilidades (Layout do Modelo)
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    
    # Cabeçalho da Tabela
    pdf.cell(110, 10, ' Habilidade', 1, 0, 'L', True)
    pdf.cell(25, 10, 'SIM', 1, 0, 'C', True)
    pdf.cell(25, 10, 'PARCIAL', 1, 0, 'C', True)
    pdf.cell(25, 10, 'NÃO', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 8)
    for _, row in dados.iterrows():
        # Texto da habilidade (ajuste de quebra de linha)
        texto_hab = f"{row['HAB_ID']} - {row['Habilidade']}"
        # Se o texto for longo, ele será cortado para manter o padrão de uma linha por item
        if len(texto_hab) > 75: texto_hab = texto_hab[:72] + "..."
        
        pdf.cell(110, 8, texto_hab.encode('latin-1', 'replace').decode('latin-1'), 1)
        pdf.cell(25, 8, str(row['SIM']), 1, 0, 'C')
        pdf.cell(25, 8, str(row['PARCIAL']), 1, 0, 'C')
        pdf.cell(25, 8, str(row['NÃO']), 1, 1, 'C')
    
    # 3. Rodapé com Totais
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 10)
    total_sim = dados['SIM'].sum()
    pdf.cell(0, 10, f"Total de Acertos (SIM): {total_sim}", 0, 1, 'R')

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- LÓGICA DO SITE ---
if uploaded_file:
    try:
        # Lê a aba de Lançamentos
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        df.columns = [str(c).strip() for c in df.columns]

        # Filtros
        st.sidebar.header("Filtros")
        sel_disc = st.sidebar.selectbox("Disciplina", sorted(df['Disciplina'].dropna().unique()))
        
        df_disc = df[df['Disciplina'] == sel_disc]
        sel_serie = st.sidebar.selectbox("Ano/Série", sorted(df_disc['Ano/Série'].dropna().unique()))
        
        df_serie = df_disc[df_disc['Ano/Série'] == sel_serie]
        sel_turma = st.sidebar.selectbox("Turma", sorted(df_serie['Turma'].dropna().unique()))

        final = df_serie[df_serie['Turma'] == sel_turma]

        if not final.empty:
            # Gráficos Visíveis no Site (Padrão de Barras Horizontais para Habilidades)
            st.write(f"### Desempenho: {sel_serie} - {sel_turma}")
            
            # Gráfico Nativo formatado
            chart_data = final.set_index('HAB_ID')[['SIM', 'PARCIAL', 'NÃO']]
            st.bar_chart(chart_data, color=["#2ecc71", "#f1c40f", "#e74c3c"]) # Cores: Verde, Amarelo, Vermelho

            st.divider()
            
            # Tabela de Conferência
            st.write("### Habilidades Avaliadas")
            st.dataframe(final[['HAB_ID', 'Habilidade', 'SIM', 'PARCIAL', 'NÃO']], use_container_width=True)

            # Botão de PDF
            pdf_bytes = gerar_pdf_modelo(final, sel_serie, sel_disc, sel_turma)
            
            st.download_button(
                label="📥 GERAR PDF (PADRÃO ESCOLA)",
                data=pdf_bytes,
                file_name=f"Relatorio_{sel_serie}_{sel_turma}.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
