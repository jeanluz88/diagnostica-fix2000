import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Carrega especificamente a aba de dados reais
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        
        # 2. Padronização técnica das colunas (remove acentos e barras)
        df.columns = [
            str(c).strip().upper()
            .replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
            .replace('Ó', 'O').replace('Ú', 'U').replace('Ã', 'A')
            .replace('/', '_').replace(' ', '_')
            for c in df.columns
        ]

        # Mapeia os nomes da sua planilha para o código
        df.rename(columns={'ANO_SERIE': 'SERIE', 'QUESTAO_ITEM': 'QUESTAO'}, inplace=True)

        # 3. Filtros na Barra Lateral
        st.sidebar.header("Filtros")
        
        lista_disc = sorted(df['DISCIPLINA'].unique())
        sel_disc = st.sidebar.selectbox("Disciplina", lista_disc)

        df_filt = df[df['DISCIPLINA'] == sel_disc]
        lista_serie = sorted(df_filt['SERIE'].unique())
        sel_serie = st.sidebar.selectbox("Série", lista_serie)

        lista_turma = sorted(df_filt[df_filt['SERIE'] == sel_serie]['TURMA'].unique())
        sel_turma = st.sidebar.selectbox("Turma", lista_turma)

        # 4. Processamento dos Dados Filtrados
        final = df_filt[(df_filt['SERIE'] == sel_serie) & (df_filt['TURMA'] == sel_turma)]

        if not final.empty:
            st.subheader(f"✅ {sel_disc} - {sel_serie} (Turma {sel_turma})")
            
            # Exibe a tabela de dados
            st.dataframe(final[['HAB_ID', 'QUESTAO', 'HABILIDADE', 'SIM', 'PARCIAL', 'NAO']], use_container_width=True)

            # --- 5. SEÇÃO DE GRÁFICOS ---
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Desempenho Geral (Pizza)")
                totais = pd.DataFrame({
                    'Status': ['SIM', 'PARCIAL', 'NÃO'],
                    'Qtd': [final['SIM'].sum(), final['PARCIAL'].sum(), final['NAO'].sum()]
                })
                fig_pizza = px.pie(totais, values='Qtd', names='Status', 
                                   color='Status', 
                                   color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NÃO':'#e74c3c'})
                st.plotly_chart(fig_pizza, use_container_width=True)

            with col2:
                st.write("### Desempenho por Questão (Barras)")
                # Gráfico de barras agrupadas por questão
                fig_barra = px.bar(final, x='QUESTAO', y=['SIM', 'PARCIAL', 'NAO'],
                                   barmode='group',
                                   color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NAO':'#e74c3c'},
                                   labels={'value': 'Alunos', 'variable': 'Nível'})
                st.plotly_chart(fig_barra, use_container_width=True)

            # --- 6. EXPORTAÇÃO ---
            st.divider()
            st.write("### 📤 Exportar Resultados")
            
            # Gerador de Excel em memória
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final.to_excel(writer, index=False, sheet_name='Resultado_Filtro')
            
            st.download_button(
                label="📥 Baixar Relatório (Excel)",
                data=output.getvalue(),
                file_name=f"Relatorio_{sel_serie}_{sel_turma}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.caption("Nota: Para gerar o PDF, abra o Excel baixado e selecione 'Salvar como PDF'.")

        else:
            st.warning("Nenhum dado encontrado para esta combinação de filtros.")

    except Exception as e:
        st.error(f"Erro ao carregar a aba 'Lancamentos': {e}")
        st.info("Verifique se o nome da aba na sua planilha é exatamente 'Lancamentos'.")
else:
    st.info("Aguardando upload da planilha NAVARRO.xlsx...")
