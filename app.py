import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

# 2. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # LER A PLANILHA: Esta é a parte crítica. 
        # Vamos ler o arquivo inteiro e depois procurar onde os dados começam.
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # Procura a linha que contém as palavras "Disciplina" ou "Série"
        # Isso ignora as linhas de "Como usar" automaticamente.
        data_start_row = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join([str(val).lower() for val in row.values])
            if 'disciplina' in row_str or 'serie' in row_str:
                data_start_row = i
                break
        
        # Relê a planilha a partir da linha correta encontrada
        df = pd.read_excel(uploaded_file, skiprows=data_start_row)
        
        # LIMPEZA TOTAL DE COLUNAS: Tira espaços, acentos e padroniza para MAIÚSCULO
        df.columns = [str(c).strip().upper().replace('É', 'E').replace('Í', 'I') for c in df.columns]

        # Verifica colunas essenciais
        col_obrigatorias = ['DISCIPLINA', 'SERIE', 'TURMA']
        if all(c in df.columns for c in col_obrigatorias):
            
            # Limpa espaços extras dentro das células
            for col in col_obrigatorias:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS ---
            st.sidebar.header("Selecione os Filtros")
            
            d_list = sorted(df['DISCIPLINA'].unique())
            d_sel = st.sidebar.selectbox("Disciplina", d_list)

            s_list = sorted(df[df['DISCIPLINA'] == d_sel]['SERIE'].unique())
            s_sel = st.sidebar.selectbox("Série", s_list)

            t_list = sorted(df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel)]['TURMA'].unique())
            t_sel = st.sidebar.selectbox("Turma", t_list)

            # --- EXIBIÇÃO ---
            dados_finais = df[(df['DISCIPLINA'] == d_sel) & 
                             (df['SERIE'] == s_sel) & 
                             (df['TURMA'] == t_sel)]
            
            st.subheader(f"📊 Resultados: {d_sel} - {s_sel} {t_sel}")
            if not dados_finais.empty:
                st.dataframe(dados_finais, use_container_width=True)
            else:
                st.warning("Selecione os filtros na barra lateral.")
        else:
            st.error(f"⚠️ Não localizamos os títulos 'Disciplina', 'Série' ou 'Turma'.")
            st.write("O sistema detectou estas colunas:", list(df.columns))

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Aguardando o upload da planilha para liberar o acesso das coordenadoras.")
