import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gerador de Relatórios", layout="wide")
st.title("📊 Painel Diagnóstico e Relatório PDF")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

# 2. FUNÇÃO DO PDF (Baseada no modelo 'Diagnostica_Final_5º ano.pdf')
def gerar_pdf(dados, serie, disciplina, turma):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Azul do Modelo
    pdf.set_fill_color(31, 73, 125)
    pdf.rect(0, 0, 210, 45, 'F')
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, 'RELATÓRIO DIAGNÓSTICO POR HABILIDADE', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 5, f'Série: {serie} | Disciplina: {disciplina} | Turma: {turma}', 0, 1, 'C')
    
    pdf.ln(25)
    pdf.set_text_color(0, 0, 0)
    
    # Tabela de Resultados
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(100, 10, 'Habilidade', 1, 0, 'L', True)
    pdf.cell(30, 10, 'SIM', 1, 0, 'C', True)
    pdf.cell(30, 10, 'PARCIAL', 1, 0, 'C', True)
    pdf.cell(30, 10, 'NÃO', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 8)
    for _, row in dados.iterrows():
        # Limita o texto da habilidade para não quebrar o layout
        texto_hab = f"{row['HAB_ID']} - {row['Habilidade']}"
        if len(texto_hab) > 65: texto_hab = texto_hab[:62] + "..."
        
        pdf.cell(100, 8, texto_hab.encode('latin-1', 'replace').decode('latin-1'), 1)
        pdf.cell(30, 8, str(row['SIM']), 1, 0, 'C')
        pdf.cell(30, 8, str(row['PARCIAL']), 1, 0, 'C')
        pdf.cell(30, 8, str(row['NÃO']), 1, 1, 'C')
        
    return pdf.output(dest='S').encode('latin-1', 'replace')

# 3. LÓGICA DO SITE
if uploaded_file:
    try:
        # Lê a aba correta sem pular linhas
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        df.columns = [str(c).strip() for c in df.columns]

        # Filtros laterais
        st.sidebar.header("Filtros do Relatório")
        sel_disc = st.sidebar.selectbox("Disciplina", sorted(df['Disciplina'].dropna().unique()))
        
        df_disc = df[df['Disciplina'] == sel_disc]
        sel_serie = st.sidebar.selectbox("Série", sorted(df_disc['Ano/Série'].dropna().unique()))
        
        df_serie = df_disc[df_disc['Ano/Série'] == sel_serie]
        sel_turma = st.sidebar.selectbox("Turma", sorted(df_serie['Turma'].dropna().unique()))

        # Filtragem Final
        final = df_serie[df_serie['Turma'] == sel_turma]

        if not final.empty:
            st.subheader(f"✅ Visualização: {sel_disc} - {sel_serie} ({sel_turma})")

            # --- GRÁFICOS VISÍVEIS NO SITE ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Desempenho por Habilidade")
                # Gráfico nativo do Streamlit (Sem Plotly)
                chart_data = final.set_index('Questão/Item')[['SIM', 'PARCIAL', 'NÃO']]
                st.bar_chart(chart_data)

            with col2:
                st.write("### Comparativo Geral (%)")
                # Gráfico de área para ver a tendência da turma
                st.area_chart(final[['SIM', 'PARCIAL', 'NÃO']])

            # Tabela de conferência
            st.write("### Dados Detalhados")
            st.dataframe(final[['Questão/Item', 'Habilidade', 'SIM', 'PARCIAL', 'NÃO']], use_container_width=True)

            # --- BOTÃO DE PDF ---
            st.divider()
            try:
                pdf_bytes = gerar_pdf(final, sel_serie, sel_disc, sel_turma)
                st.download_button(
                    label="📥 EMITIR RELATÓRIO EM PDF",
                    data=pdf_bytes,
                    file_name=f"Relatorio_{sel_serie}_{sel_turma}.pdf",
                    mime="application/pdf"
                )
            except Exception as e_pdf:
                st.error(f"Erro ao gerar PDF: {e_pdf}")

    except Exception as e:
        st.error(f"Erro ao ler planilha: {e}")
else:
    st.info("Aguardando upload da planilha NAVARRO.xlsx...")
