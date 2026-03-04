import streamlit as st
import pandas as pd

# 1. Configuração Total
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # LER SEM CABEÇALHO PARA ESCANEAR A PLANILHA
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # LOCALIZADOR DE DADOS: Procura a linha que contém os títulos reais
        linha_inicio = 0
        for i, row in df_raw.iterrows():
            texto_linha = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
            if 'DISCIPLINA' in texto_linha and 'SERIE' in texto_linha:
                linha_inicio = i
                break
        
        # Carrega os dados ignorando as linhas inúteis do topo
        df = pd.read_excel(uploaded_file, skiprows=linha_inicio)
        
        # Limpa nomes de colunas (remove espaços e acentos)
        df.columns = [str(c).strip().upper().replace('É', 'E').replace('Í', 'I') for c in df.columns]

        # Colunas obrigatórias
        cols_vivas = ['DISCIPLINA', 'SERIE', 'TURMA']
        
        if all(c in df.columns for c in cols_vivas):
            # Limpa os dados internos
            for c in cols_vivas:
                df[c] = df[c].astype(str).str.strip()

            # --- FILTROS ---
            st.sidebar.header("Selecione os Dados")
            
            d_list = sorted(df['DISCIPLINA'].unique())
            d_sel = st.sidebar.selectbox("Disciplina", d_list)

            s_list = sorted(df[df['DISCIPLINA'] == d_sel]['SERIE'].unique())
            s_sel = st.sidebar.selectbox("Série", s_list)

            t_list = sorted(df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel)]['TURMA'].unique())
            t_sel = st.sidebar.selectbox("Turma", t_list)

            # --- RESULTADO ---
            exibir = df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel) & (df['TURMA'] == t_sel)]
            
            st.subheader(f"✅ Exibindo resultados de {d_sel}")
            st.dataframe(exibir, use_container_width=True)
            
        else:
            st.error("⚠️ Não foi possível localizar as colunas de dados.")
            st.info(f"O sistema tentou ler a partir da linha {linha_inicio + 1}, mas não achou os títulos certos.")

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
else:
    st.info("Aguardando o upload da planilha...")
