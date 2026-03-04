import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # Lê o arquivo focando na aba 'Lancamentos'
        # O parâmetro header=0 assume que a linha de títulos está logo antes dos dados
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        
        # Padroniza os nomes das colunas para evitar KeyError
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Mapeamento para garantir que o sistema encontre as colunas
        mapa = {
            'ANO/SÉRIE': 'ANO/SERIE',
            'DISCIPLINA': 'DISCIPLINA',
            'TURMA': 'TURMA'
        }
        df.rename(columns=mapa, inplace=True)

        # Filtros necessários
        st.sidebar.header("Filtros")
        
        # 1. Filtro de Disciplina
        disc_list = sorted(df['DISCIPLINA'].dropna().unique())
        disc_sel = st.sidebar.selectbox("Disciplina", disc_list)

        # 2. Filtro de Série
        serie_list = sorted(df[df['DISCIPLINA'] == disc_sel]['ANO/SERIE'].dropna().unique())
        serie_sel = st.sidebar.selectbox("Ano/Série", serie_list)

        # 3. Filtro de Turma
        turma_list = sorted(df[(df['DISCIPLINA'] == disc_sel) & (df['ANO/SERIE'] == serie_sel)]['TURMA'].dropna().unique())
        turma_sel = st.sidebar.selectbox("Turma", turma_list)

        # Exibição dos dados filtrados
        dados = df[(df['DISCIPLINA'] == disc_sel) & 
                   (df['ANO/SERIE'] == serie_sel) & 
                   (df['TURMA'] == turma_sel)]
        
        st.subheader(f"Resultados: {disc_sel} - {serie_sel} (Turma {turma_sel})")
        st.dataframe(dados, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
        st.info("Dica: Certifique-se de que a aba se chama exatamente 'Lancamentos'.")
else:
    st.info("Aguardando upload da planilha.")
