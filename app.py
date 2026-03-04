import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # Lemos a planilha bruta sem considerar cabeçalhos
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # BUSCA AUTOMÁTICA: Varre as linhas para achar 'DISCIPLINA' ou 'SERIE'
        # Isso ignora qualquer texto de instrução que esteja no topo da planilha
        start_row = 0
        for i, row in df_raw.iterrows():
            linha_texto = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
            if 'DISCIPLINA' in linha_texto and 'SERIE' in linha_texto:
                start_row = i
                break
        
        # Relê o arquivo a partir da linha correta
        df = pd.read_excel(uploaded_file, skiprows=start_row)
        
        # Limpa nomes de colunas: remove espaços e padroniza acentos
        df.columns = [str(c).strip().upper().replace('É', 'E').replace('Í', 'I') for c in df.columns]

        # Verifica se as 3 colunas vitais existem
        cols_vivas = ['DISCIPLINA', 'SERIE', 'TURMA']
        if all(c in df.columns for c in cols_vivas):
            
            # Limpa espaços dentro das células
            for c in cols_vivas:
                df[c] = df[c].astype(str).str.strip()

            # --- FILTROS LATERAIS ---
            st.sidebar.header("Filtros")
            
            d_list = sorted(df['DISCIPLINA'].unique())
            d_sel = st.sidebar.selectbox("Disciplina", d_list)

            s_list = sorted(df[df['DISCIPLINA'] == d_sel]['SERIE'].unique())
            s_sel = st.sidebar.selectbox("Série", s_list)

            t_list = sorted(df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel)]['TURMA'].unique())
            t_sel = st.sidebar.selectbox("Turma", t_list)

            # --- EXIBIÇÃO DOS DADOS ---
            final = df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel) & (df['TURMA'] == t_sel)]
            
            st.subheader(f"✅ Exibindo: {d_sel} - {s_sel} {t_sel}")
            st.dataframe(final, use_container_width=True)
            
        else:
            st.error("⚠️ Títulos das colunas não encontrados.")
            st.write("O sistema detectou estas colunas:", list(df.columns))
            st.info("Verifique se os nomes 'Disciplina', 'Série' e 'Turma' estão na planilha.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Aguardando upload da planilha...")
