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
        # 1. Carrega os dados da aba correta (Lancamentos)
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        
        # 2. Padronização total das colunas para o código não se perder
        df.columns = [
            str(c).strip().upper()
            .replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
            .replace('Ó', 'O').replace('Ú', 'U').replace('Ã', 'A')
            .replace('/', '_').replace(' ', '_').replace('%', 'PORC_')
            for c in df.columns
        ]

        # Mapeamento de nomes específicos da sua planilha
        df.rename(columns={'ANO_SERIE': 'SERIE', 'NAO': 'NAO_COL'}, inplace=True)

        # 3. Filtros Laterais
        st.sidebar.header("Filtros de Busca")
        
        lista_disc = sorted(df['DISCIPLINA'].unique())
        sel_disc = st.sidebar.selectbox("Disciplina", lista_disc)

        df_filt = df[df['DISCIPLINA'] == sel_disc]
        lista_serie = sorted(df_filt['SERIE'].unique())
        sel_serie = st.sidebar.selectbox("Série", lista_serie)

        lista_turma = sorted(df_filt[df_filt['SERIE'] == sel_serie]['TURMA'].unique())
        sel_turma = st.sidebar.selectbox("Turma", lista_turma)

        # 4. Dados Filtrados
        final = df_filt[(df_filt['SERIE'] == sel_serie) & (df_filt['TURMA'] == sel_turma)]

        if not final.empty:
            st.subheader(f"✅ {sel_disc} - {sel_serie} (Turma {sel_turma})")
            
            # Exibe a tabela
            st.dataframe(final[['HAB_ID', 'QUESTAO_ITEM', 'HABILIDADE', 'SIM', 'PARCIAL', 'NAO_COL']], use_container_width=True)

            st.divider()

            # --- 5. GRÁFICOS (PLOTLY) ---
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Desempenho Geral")
                totais = {
                    'Status': ['SIM', 'PARCIAL', 'NÃO'],
                    'Qtd': [final['SIM'].sum(), final['PARCIAL'].sum(), final['NAO_COL'].sum()]
                }
                resumo = pd.DataFrame(totais)
                fig_pizza = px.pie(resumo, values='Qtd', names='Status', 
                                   color='Status', 
                                   color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NÃO':'#e74c3c'})
                st.plotly_chart(fig_pizza, use_container_width=True)

            with col2:
                st.write("### Desempenho por Questão")
                fig_barra = px.bar(final, x='QUESTAO_ITEM', y=['SIM', 'PARCIAL', 'NAO_COL'],
                                   barmode='group',
                                   color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NAO_COL':'#e74c3c'},
                                   labels={'value': 'Alunos', 'QUESTAO_ITEM': 'Questão'})
                st.plotly_chart(fig_barra, use_container_width=True)

            # --- 6. EXPORTAÇÃO (Solução estável) ---
            st.divider()
            st.write("### 📤 Gerar Relatório")
            
            # Criar um buffer para o Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final.to_excel(writer, index=False, sheet_name='Relatorio')
            
            st.download_button(
                label="📥 Baixar Relatório em Excel",
                data=output.getvalue(),
                file_name=f"Resultado_{sel_serie}_{sel_turma}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.caption("Nota: Para PDF, salve o arquivo Excel como PDF no seu computador.")

        else:
            st.warning("Nenhum dado encontrado.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("Aguardando upload da planilha NAVARRO.xlsx...")
