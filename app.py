import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")

# Título Principal
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Carrega os dados da aba correta
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        
        # 2. Padronização de Colunas (Trata "Ano/Série" e acentos)
        df.columns = [
            str(c).strip().upper()
            .replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
            .replace('Ó', 'O').replace('Ú', 'U')
            .replace('/', '_').replace(' ', '_')
            for c in df.columns
        ]

        # Mapeamento para o código reconhecer as colunas da sua planilha
        df.rename(columns={'ANO_SERIE': 'SERIE'}, inplace=True)

        # 3. Filtros Laterais
        st.sidebar.header("Selecione os Filtros")
        
        lista_disc = sorted(df['DISCIPLINA'].unique())
        sel_disc = st.sidebar.selectbox("Disciplina", lista_disc)

        df_filt = df[df['DISCIPLINA'] == sel_disc]
        lista_serie = sorted(df_filt['SERIE'].unique())
        sel_serie = st.sidebar.selectbox("Série", lista_serie)

        lista_turma = sorted(df_filt[df_filt['SERIE'] == sel_serie]['TURMA'].unique())
        sel_turma = st.sidebar.selectbox("Turma", lista_turma)

        # 4. Filtragem Final
        dados_finais = df_filt[(df_filt['SERIE'] == sel_serie) & (df_filt['TURMA'] == sel_turma)]

        if not dados_finais.empty:
            # Exibição da Tabela
            st.subheader(f"✅ Resultados: {sel_disc} - {sel_serie} (Turma {sel_turma})")
            st.dataframe(dados_finais[['HAB_ID', 'QUESTAO_ITEM', 'HABILIDADE', 'SIM', 'PARCIAL', 'NAO']], use_container_width=True)

            # --- 5. GRÁFICOS ( plotly ) ---
            st.divider()
            col1, col2 = st.columns(2)

            # Cálculo de totais para o gráfico
            total_sim = dados_finais['SIM'].sum()
            total_parcial = dados_finais['PARCIAL'].sum()
            total_nao = dados_finais['NAO'].sum()

            resumo_grafico = pd.DataFrame({
                'Status': ['SIM', 'PARCIAL', 'NÃO'],
                'Total': [total_sim, total_parcial, total_nao]
            })

            with col1:
                st.write("### Desempenho Geral (Pizza)")
                fig_pizza = px.pie(resumo_grafico, values='Total', names='Status', 
                                   color='Status', color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NÃO':'#e74c3c'})
                st.plotly_chart(fig_pizza, use_container_width=True)

            with col2:
                st.write("### Desempenho por Habilidade (Barras)")
                fig_barra = px.bar(dados_finais, x='HAB_ID', y=['SIM', 'PARCIAL', 'NAO'],
                                   title="Resultados por Item", barmode='group')
                st.plotly_chart(fig_barra, use_container_width=True)

            # --- 6. BOTÃO DE EXPORTAÇÃO (Excel/CSV como alternativa ao PDF direto no navegador) ---
            st.divider()
            st.write("### 📤 Exportar Relatório")
            
            # Gerar CSV para download rápido (substituindo PDF que exige bibliotecas complexas no servidor)
            csv = dados_finais.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar Relatório em CSV",
                data=csv,
                file_name=f"Relatorio_{sel_serie}_{sel_turma}.csv",
                mime="text/csv",
            )
            st.info("O formato CSV pode ser aberto no Excel e salvo como PDF facilmente.")

        else:
            st.warning("Nenhum dado encontrado para essa seleção.")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("Aguardando upload da planilha NAVARRO.xlsx...")
