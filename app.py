import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

arquivo = st.file_uploader("Carregue a planilha NAVARRO.xlsx", type=["xlsx"])

if arquivo:
    try:
        # LER DIRETO: O ficheiro Lancamentos.csv que enviaste mostra que
        # os títulos estão na linha 0. Não se pula nada.
        df = pd.read_excel(arquivo, sheet_name='Lancamentos')

        # FILTROS LATERAIS (Usando os nomes exatos das tuas colunas)
        st.sidebar.header("Filtros")
        
        # 1. Disciplina
        disciplinas = sorted(df['Disciplina'].dropna().unique())
        escolha_disc = st.sidebar.selectbox("Disciplina", disciplinas)

        # 2. Ano/Série (Filtrado pela disciplina anterior)
        df_aux = df[df['Disciplina'] == escolha_disc]
        series = sorted(df_aux['Ano/Série'].dropna().unique())
        escolha_serie = st.sidebar.selectbox("Ano/Série", series)

        # 3. Turma
        turmas = sorted(df_aux[df_aux['Ano/Série'] == escolha_serie]['Turma'].dropna().unique())
        escolha_turma = st.sidebar.selectbox("Turma", turmas)

        # FILTRAGEM FINAL
        resultado = df_aux[(df_aux['Ano/Série'] == escolha_serie) & (df_aux['Turma'] == escolha_turma)]

        if not resultado.empty:
            st.subheader(f"✅ Resultados: {escolha_disc} - {escolha_serie} ({escolha_turma})")
            
            # Mostrar a tabela com as colunas de dados
            st.dataframe(resultado[['Questão/Item', 'Habilidade', 'SIM', 'PARCIAL', 'NÃO']], use_container_width=True)

            # --- GRÁFICOS ---
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Total Geral")
                # Soma os valores de SIM, PARCIAL e NÃO da seleção
                somas = pd.DataFrame({
                    'Avaliação': ['SIM', 'PARCIAL', 'NÃO'],
                    'Total': [resultado['SIM'].sum(), resultado['PARCIAL'].sum(), resultado['NÃO'].sum()]
                })
                fig_pizza = px.pie(somas, values='Total', names='Avaliação', 
                                   color='Avaliação',
                                   color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NÃO':'#e74c3c'})
                st.plotly_chart(fig_pizza, use_container_width=True)

            with col2:
                st.write("### Detalhado por Questão")
                fig_barra = px.bar(resultado, x='Questão/Item', y=['SIM', 'PARCIAL', 'NÃO'],
                                   barmode='group',
                                   color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NÃO':'#e74c3c'})
                st.plotly_chart(fig_barra, use_container_width=True)

            # --- EXPORTAÇÃO EXCEL ---
            st.divider()
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                resultado.to_excel(writer, index=False, sheet_name='Relatorio')
            
            st.download_button(
                label="📥 Baixar Relatório em Excel",
                data=buffer.getvalue(),
                file_name=f"Relatorio_{escolha_serie}_{escolha_turma}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Erro ao ler a aba 'Lancamentos'. Detalhe: {e}")
else:
    st.info("Aguardando a planilha para exibir os dados das coordenadoras.")
