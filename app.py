import streamlit as st
import pandas as pd

# Configuração básica
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

# Upload do arquivo
uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # Lendo a planilha (Garante leitura de qualquer aba)
        df = pd.read_excel(uploaded_file)
        
        # LIMPEZA TOTAL DE COLUNAS: Tira espaços, acentos e deixa tudo MAIÚSCULO
        # Isso resolve o erro de não achar 'Serie' ou 'Série'
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.rename(columns={'SÉRIE': 'SERIE', 'DISCIPLINA': 'DISCIPLINA', 'TURMA': 'TURMA', 'RESULTADO': 'RESULTADO'})

        # Verifica se as colunas básicas existem
        colunas_vivas = ['DISCIPLINA', 'SERIE', 'TURMA']
        if all(c in df.columns for c in colunas_vivas):
            
            # Limpeza dos dados para evitar duplicados no filtro
            for c in colunas_vivas:
                df[c] = df[c].astype(str).str.strip()

            # --- FILTROS (Sem duplicados com .unique()) ---
            st.sidebar.header("Filtros")
            
            disc_lista = sorted(df['DISCIPLINA'].unique())
            disc_sel = st.sidebar.selectbox("Disciplina", disc_lista)

            serie_lista = sorted(df[df['DISCIPLINA'] == disc_sel]['SERIE'].unique())
            serie_sel = st.sidebar.selectbox("Série", serie_lista)

            turma_lista = sorted(df[(df['DISCIPLINA'] == disc_sel) & (df['SERIE'] == serie_sel)]['TURMA'].unique())
            turma_sel = st.sidebar.selectbox("Turma", turma_lista)

            # Filtragem final
            dados = df[(df['DISCIPLINA'] == disc_sel) & (df['SERIE'] == serie_sel) & (df['TURMA'] == turma_sel)]

            # --- EXIBIÇÃO SIMPLES ---
            st.subheader(f"Resultados: {disc_sel} - {serie_sel} {turma_sel}")
            
            if not dados.empty:
                st.dataframe(dados, use_container_width=True)
            else:
                st.warning("Nenhum dado encontrado para esta seleção.")
        else:
            st.error(f"Colunas lidas: {list(df.columns)}")
            st.warning("A planilha precisa ter as colunas: Disciplina, Serie e Turma.")

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    st.info("Por favor, faça o upload da planilha para liberar os filtros.")
