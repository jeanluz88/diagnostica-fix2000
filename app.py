import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

# 2. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # LER A PLANILHA BRUTA (sem cabeçalho) para localizar os dados reais
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # BUSCA DINÂMICA: Varre as linhas para achar 'Disciplina' ou 'Série'
        # Isso ignora automaticamente qualquer texto de "instrução" no topo
        start_row = 0
        for i, row in df_raw.iterrows():
            linha_texto = " ".join([str(v).lower() for v in row.values])
            if 'disciplina' in linha_texto or 'serie' in linha_texto:
                start_row = i
                break
        
        # Relê o arquivo a partir da linha correta encontrada
        df = pd.read_excel(uploaded_file, skiprows=start_row)
        
        # NORMALIZAÇÃO DE COLUNAS: Remove espaços e trata acentos
        df.columns = [
            str(c).strip().upper()
            .replace('É', 'E').replace('Í', 'I').replace('Á', 'A') 
            for c in df.columns
        ]

        # Colunas essenciais para o funcionamento
        cols_alvo = ['DISCIPLINA', 'SERIE', 'TURMA']
        
        if all(c in df.columns for c in cols_alvo):
            # Limpa espaços extras dentro das células
            for col in cols_alvo:
                df[col] = df[col].astype(str).str.strip()

            # --- SISTEMA DE FILTROS ---
            st.sidebar.header("Filtros")
            
            d_list = sorted(df['DISCIPLINA'].unique())
            d_sel = st.sidebar.selectbox("Escolha a Disciplina", d_list)

            s_list = sorted(df[df['DISCIPLINA'] == d_sel]['SERIE'].unique())
            s_sel = st.sidebar.selectbox("Escolha a Série", s_list)

            t_list = sorted(df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel)]['TURMA'].unique())
            t_sel = st.sidebar.selectbox("Escolha a Turma", t_list)

            # --- EXIBIÇÃO ---
            dados_finais = df[(df['DISCIPLINA'] == d_sel) & 
                             (df['SERIE'] == s_sel) & 
                             (df['TURMA'] == t_sel)]
            
            st.subheader(f"✅ Resultados para: {d_sel} - {s_sel} {t_sel}")
            st.dataframe(dados_finais, use_container_width=True)
            
        else:
            st.error("⚠️ Não foi possível localizar as colunas de dados.")
            st.write("O sistema detectou estas colunas na linha de dados:", list(df.columns))
            st.info("Verifique se as colunas 'Disciplina' e 'Série' estão escritas corretamente.")

    except Exception as e:
        st.error(f"Erro técnico ao ler o arquivo: {e}")
else:
    st.info("Aguardando upload da planilha para liberar os filtros.")
