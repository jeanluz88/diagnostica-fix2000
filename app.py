import streamlit as st
import pandas as pd

# 1. Configuração de Página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

# 2. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # Lemos a planilha sem considerar cabeçalhos para "escanear" o arquivo
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # BUSCA DINÂMICA: Varre as linhas até achar onde está escrito 'DISCIPLINA'
        # Isso pula automaticamente qualquer aviso ou instrução no topo
        start_row = 0
        for i, row in df_raw.iterrows():
            linha_texto = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
            if 'DISCIPLINA' in linha_texto and 'SERIE' in linha_texto:
                start_row = i
                break
        
        # Relê o arquivo a partir da linha de dados correta encontrada
        df = pd.read_excel(uploaded_file, skiprows=start_row)
        
        # Limpa nomes de colunas: remove espaços e trata acentos
        df.columns = [str(c).strip().upper().replace('É', 'E').replace('Í', 'I') for c in df.columns]

        # Colunas vitais para o funcionamento
        cols_vitais = ['DISCIPLINA', 'SERIE', 'TURMA']
        
        if all(c in df.columns for c in cols_vitais):
            # Limpa espaços extras dentro das células de dados
            for c in cols_vitais:
                df[c] = df[c].astype(str).str.strip()

            # --- SISTEMA DE FILTROS ---
            st.sidebar.header("Filtros de Busca")
            
            d_list = sorted(df['DISCIPLINA'].unique())
            d_sel = st.sidebar.selectbox("1. Escolha a Disciplina", d_list)

            s_list = sorted(df[df['DISCIPLINA'] == d_sel]['SERIE'].unique())
            s_sel = st.sidebar.selectbox("2. Escolha a Série", s_list)

            t_list = sorted(df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel)]['TURMA'].unique())
            t_sel = st.sidebar.selectbox("3. Escolha a Turma", t_list)

            # --- EXIBIÇÃO ---
            resultado = df[(df['DISCIPLINA'] == d_sel) & 
                          (df['SERIE'] == s_sel) & 
                          (df['TURMA'] == t_sel)]
            
            st.subheader(f"✅ Resultados encontrados para: {d_sel}")
            st.dataframe(resultado, use_container_width=True)
            
        else:
            st.error("⚠️ Não foi possível localizar as colunas de dados.")
            st.info("O sistema tentou ler a planilha, mas não achou os títulos 'Disciplina' e 'Série'.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Aguardando o upload da planilha para liberar os filtros.")
