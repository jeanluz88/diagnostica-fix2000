import streamlit as st
import pandas as pd

# 1. Configuração de Página Estável
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # Lemos a planilha bruta sem considerar cabeçalhos inicialmente
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # BUSCA DINÂMICA: Varre as linhas até encontrar 'DISCIPLINA' ou 'SERIE'
        # Isso ignora textos de instrução ou títulos mesclados no topo automaticamente
        start_row = 0
        for i, row in df_raw.iterrows():
            linha_txt = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
            if 'DISCIPLINA' in linha_txt or 'SERIE' in linha_txt:
                start_row = i
                break
        
        # Relê o arquivo a partir da linha correta identificada
        df = pd.read_excel(uploaded_file, skiprows=start_row)
        
        # NORMALIZAÇÃO: Remove espaços e trata acentos nos nomes das colunas
        df.columns = [
            str(c).strip().upper()
            .replace('É', 'E').replace('Í', 'I').replace('Á', 'A') 
            for c in df.columns
        ]

        # Colunas essenciais para o funcionamento
        cols_alvo = ['DISCIPLINA', 'SERIE', 'TURMA']
        
        if all(c in df.columns for c in cols_alvo):
            # Limpa espaços extras dentro das células de dados
            for col in cols_alvo:
                df[col] = df[col].astype(str).str.strip()

            # --- SISTEMA DE FILTROS ---
            st.sidebar.header("Filtros de Seleção")
            
            # Filtros dinâmicos e encadeados
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
            
            st.subheader(f"✅ Resultados: {d_sel} - {s_sel} {t_sel}")
            st.dataframe(resultado, use_container_width=True)
            
        else:
            st.error("⚠️ Não conseguimos localizar as colunas de dados.")
            st.write("Colunas detectadas pelo sistema:", list(df.columns))
            st.info("Verifique se os títulos 'Disciplina', 'Série' e 'Turma' estão na planilha.")

    except Exception as e:
        st.error(f"Erro técnico ao processar o arquivo: {e}")
else:
    st.info("Aguardando o upload da planilha para liberar o acesso das coordenadoras.")
