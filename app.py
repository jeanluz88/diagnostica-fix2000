import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

# Upload do arquivo
uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Carrega o Excel sem considerar nenhum cabeçalho para análise bruta
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # 2. Busca exaustiva pela linha que contém os dados reais
        # Procuramos por 'DISCIPLINA' em qualquer lugar da planilha
        start_row = None
        for i, row in df_raw.iterrows():
            linha_completa = " ".join([str(val).upper() for val in row.values if pd.notna(val)])
            if 'DISCIPLINA' in linha_completa:
                start_row = i
                break
        
        if start_row is not None:
            # 3. Relê a planilha a partir da linha encontrada
            df = pd.read_excel(uploaded_file, skiprows=start_row)
            
            # 4. Limpeza radical de nomes de colunas (tira espaços, acentos e põe em maiúsculo)
            df.columns = [
                str(c).strip().upper()
                .replace('É', 'E').replace('Í', 'I').replace('Á', 'A').replace('Ó', 'O')
                for c in df.columns
            ]

            # 5. Verifica as colunas mínimas para o filtro
            cols_necessarias = ['DISCIPLINA', 'SERIE', 'TURMA']
            if all(c in df.columns for c in cols_necessarias):
                
                # Limpa os dados das colunas de filtro
                for c in cols_necessarias:
                    df[c] = df[c].astype(str).str.strip()

                # Interface de Filtros
                st.sidebar.header("Filtros")
                disc_list = sorted(df['DISCIPLINA'].unique())
                disc_sel = st.sidebar.selectbox("Disciplina", disc_list)

                serie_list = sorted(df[df['DISCIPLINA'] == disc_sel]['SERIE'].unique())
                serie_sel = st.sidebar.selectbox("Série", serie_list)

                turma_list = sorted(df[(df['DISCIPLINA'] == disc_sel) & (df['SERIE'] == serie_sel)]['TURMA'].unique())
                turma_sel = st.sidebar.selectbox("Turma", turma_list)

                # Resultado Final
                dados_filtrados = df[(df['DISCIPLINA'] == disc_sel) & 
                                    (df['SERIE'] == serie_sel) & 
                                    (df['TURMA'] == turma_sel)]
                
                st.subheader(f"✅ Exibindo: {disc_sel} | {serie_sel} {turma_sel}")
                st.dataframe(dados_filtrados, use_container_width=True)
                
            else:
                st.error("⚠️ Títulos não encontrados na linha de dados.")
                st.write("Colunas detectadas:", list(df.columns))
        else:
            st.error("❌ Não foi possível localizar a palavra 'DISCIPLINA' na planilha.")
            st.info("O sistema varreu todas as linhas e não encontrou o cabeçalho de dados.")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
else:
    st.info("Aguardando upload da planilha...")
