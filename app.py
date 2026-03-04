import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # Lê a planilha bruta para localizar os cabeçalhos reais
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # Localiza a linha que contém as colunas de dados
        start_row = 0
        for i, row in df_raw.iterrows():
            linha_txt = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
            if 'DISCIPLINA' in linha_txt and 'SERIE' in linha_txt:
                start_row = i
                break
        
        # Carrega os dados ignorando o lixo do topo
        df = pd.read_excel(uploaded_file, skiprows=start_row)
        
        # Normaliza nomes de colunas (tira espaços e acentos)
        df.columns = [
            str(c).strip().upper()
            .replace('É', 'E').replace('Í', 'I').replace('Á', 'A') 
            for c in df.columns
        ]

        # Colunas necessárias
        cols_vitais = ['DISCIPLINA', 'SERIE', 'TURMA']
        
        if all(c in df.columns for c in cols_vitais):
            for col in cols_vitais:
                df[col] = df[col].astype(str).str.strip()

            # Filtros laterais
            st.sidebar.header("Filtros")
            
            d_list = sorted(df['DISCIPLINA'].unique())
            d_sel = st.sidebar.selectbox("Disciplina", d_list)

            s_list = sorted(df[df['DISCIPLINA'] == d_sel]['SERIE'].unique())
            s_sel = st.sidebar.selectbox("Série", s_list)

            t_list = sorted(df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel)]['TURMA'].unique())
            t_sel = st.sidebar.selectbox("Turma", t_list)

            # Filtragem e Exibição
            df_final = df[(df['DISCIPLINA'] == d_sel) & 
                          (df['SERIE'] == s_sel) & 
                          (df['TURMA'] == t_sel)]
            
            st.subheader(f"✅ {d_sel} - {s_sel} {t_sel}")
            st.dataframe(df_final, use_container_width=True)
            
        else:
            st.error(f"Erro: Colunas não encontradas. Detectadas: {list(df.columns)}")

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.info("Aguardando upload da planilha.")
