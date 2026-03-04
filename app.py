import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configurações iniciais
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Lendo a aba específica de dados
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')

        # 2. Normalização técnica de colunas (Remove acentos, espaços e caracteres especiais)
        # Isso garante que 'Ano/Série' vire 'ANO_SERIE' e 'NÃO' vire 'NAO'
        df.columns = [
            str(c).strip().upper()
            .replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
            .replace('Ó', 'O').replace('Ú', 'U').replace('Ã', 'A')
            .replace('/', '_').replace(' ', '_').replace('.', '_')
            for c in df.columns
        ]

        # Mapeia os nomes corrigidos para o uso no código
        df.rename(columns={'ANO_SERIE': 'SERIE', 'QUESTAO_ITEM': 'QUESTAO'}, inplace=True)

        # 3. Filtros Laterais dinâmicos
        st.sidebar.header("Filtros de Pesquisa")
        
        lista_disc = sorted(df['DISCIPLINA'].dropna().unique())
        sel_disc = st.sidebar.selectbox("Escolha a Disciplina", lista_disc)

        df_filt_disc = df[df['DISCIPLINA'] == sel_disc]
        lista_serie = sorted(df_filt_disc['SERIE'].dropna().unique())
        sel_serie = st.sidebar.selectbox("Escolha a Série", lista_serie)

        df_filt_serie = df_filt_disc[df_filt_disc['SERIE'] == sel_serie]
        lista_turma = sorted(df_filt_serie['TURMA'].dropna().unique())
        sel_turma = st.sidebar.selectbox("Escolha a Turma", lista_turma)

        # 4. Seleção Final dos Dados
        dados_finais = df_filt_serie[df_filt_serie['TURMA'] == sel_turma]

        if not dados_finais.empty:
            st.subheader(f"✅ Resultados: {sel_disc} - {sel_serie} (Turma {sel_turma})")
            
            # Tabela de dados principais
            cols_ver = ['HAB_ID', 'QUESTAO', 'HABILIDADE', 'SIM', 'PARCIAL', 'NAO']
            st.dataframe(dados_finais[cols_ver], use_container_width=True)

            # --- 5. GRÁFICOS INTERATIVOS ---
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.write("### Desempenho Geral (Pizza)")
                totais = pd.DataFrame({
                    'Status': ['SIM', 'PARCIAL', 'NÃO'],
                    'Votos': [dados_finais['SIM'].sum(), dados_finais['PARCIAL'].sum(), dados_finais['NAO'].sum()]
                })
                fig_pie = px.pie(totais, values='Votos', names='Status', 
                                 color='Status',
                                 color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NÃO':'#e74c3c'})
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.write("### Desempenho por Questão (Barras)")
                # Gráfico de barras agrupadas
                fig_bar = px.bar(dados_finais, x='QUESTAO', y=['SIM', 'PARCIAL', 'NAO'],
                                 barmode='group',
                                 color_discrete_map={'SIM':'#2ecc71', 'PARCIAL':'#f1c40f', 'NAO':'#e74c3c'},
                                 labels={'value': 'Qtd Alunos', 'variable': 'Avaliação'})
                st.plotly_chart(fig_bar, use_container_width=True)

            # --- 6. EXPORTAR PARA EXCEL (Alternativa robusta ao PDF) ---
            st.divider()
            st.write("### 📤 Gerar Relatório")
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                dados_finais.to_excel(writer, index=False, sheet_name='Relatorio')
            
            st.download_button(
                label="📥 Baixar Dados em Excel",
                data=output.getvalue(),
                file_name=f"Relatorio_{sel_serie}_{sel_turma}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.caption("As coordenadoras podem salvar o Excel como PDF após o download.")

        else:
            st.warning("Nenhum dado encontrado para os filtros aplicados.")

    except Exception as e:
        st.error(f"Erro ao processar planilha: {e}")
else:
    st.info("Aguardando upload da planilha NAVARRO.xlsx...")
