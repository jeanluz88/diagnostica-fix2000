import streamlit as st
import pandas as pd
from io import BytesIO

# Configuração de Página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Carregue a planilha NAVARRO.xlsx", type=["xlsx"])

if uploaded_file:
    try:
        # Lendo a aba de lançamentos (Os títulos estão na linha 1 / Índice 0)
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')

        # Limpeza de nomes de colunas
        df.columns = [str(c).strip() for c in df.columns]

        # FILTROS LATERAIS
        st.sidebar.header("Filtros")
        
        # 1. Filtro de Disciplina
        lista_disc = sorted(df['Disciplina'].dropna().unique())
        sel_disc = st.sidebar.selectbox("Selecione a Disciplina", lista_disc)

        # 2. Filtro de Ano/Série
        df_aux = df[df['Disciplina'] == sel_disc]
        lista_serie = sorted(df_aux['Ano/Série'].dropna().unique())
        sel_serie = st.sidebar.selectbox("Selecione o Ano/Série", lista_serie)

        # 3. Filtro de Turma
        lista_turma = sorted(df_aux[df_aux['Ano/Série'] == sel_serie]['Turma'].dropna().unique())
        sel_turma = st.sidebar.selectbox("Selecione a Turma", lista_turma)

        # PROCESSAMENTO DOS DADOS FILTRADOS
        final = df_aux[(df_aux['Ano/Série'] == sel_serie) & (df_aux['Turma'] == sel_turma)]

        if not final.empty:
            st.subheader(f"✅ {sel_disc} - {sel_serie} (Turma {sel_turma})")
            
            # Tabela de dados
            st.dataframe(final[['Questão/Item', 'Habilidade', 'SIM', 'PARCIAL', 'NÃO']], use_container_width=True)

            st.divider()

            # --- GRÁFICOS NATIVOS (SEM PLOTLY) ---
            st.write("### Resumo de Desempenho")
            
            # Criando um gráfico de barras simples do próprio Streamlit
            chart_data = final.set_index('Questão/Item')[['SIM', 'PARCIAL', 'NÃO']]
            st.bar_chart(chart_data)

            # --- EXPORTAÇÃO EXCEL ---
            st.divider()
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final.to_excel(writer, index=False, sheet_name='Resultado')
            
            st.download_button(
                label="📥 Baixar Relatório (Excel)",
                data=output.getvalue(),
                file_name=f"Relatorio_{sel_serie}_{sel_turma}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Selecione os filtros acima para visualizar os dados.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("Aguardando o upload da planilha.")
