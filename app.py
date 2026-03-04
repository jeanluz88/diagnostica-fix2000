import streamlit as st
import pandas as pd

# Configuração essencial
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Leitura bruta para encontrar onde os dados começam
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # 2. Busca automática pela linha do cabeçalho real
        start_row = 0
        for i, row in df_raw.iterrows():
            # Converte a linha em texto e procura por palavras-chave
            linha_txt = " ".join([str(v).upper() for v in row.values if pd.notna(v)])
            if 'DISCIPLINA' in linha_txt and 'SERIE' in linha_txt:
                start_row = i
                break
        
        # 3. Carrega os dados reais a partir da linha encontrada
        df = pd.read_excel(uploaded_file, skiprows=start_row)
        
        # 4. Limpeza e Padronização de Colunas (remove espaços e acentos)
        df.columns = [str(c).strip().upper().replace('É', 'E').replace('Í', 'I') for c in df.columns]

        # Colunas que o sistema precisa para filtrar
        cols_alvo = ['DISCIPLINA', 'SERIE', 'TURMA']
        
        if all(c in df.columns for c in cols_alvo):
            # Garante que os dados dentro das células também estejam limpos
            for col in cols_alvo:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS LATERAIS ---
            st.sidebar.header("Filtros de Busca")
            
            # Filtro de Disciplina
            lista_d = sorted(df['DISCIPLINA'].unique())
            sel_d = st.sidebar.selectbox("Selecione a Disciplina", lista_d)

            # Filtro de Série (baseado na disciplina)
            lista_s = sorted(df[df['DISCIPLINA'] == sel_d]['SERIE'].unique())
            sel_s = st.sidebar.selectbox("Selecione a Série", lista_s)

            # Filtro de Turma (baseado nos anteriores)
            lista_t = sorted(df[(df['DISCIPLINA'] == sel_d) & (df['SERIE'] == sel_s)]['TURMA'].unique())
            sel_t = st.sidebar.selectbox("Selecione a Turma", lista_t)

            # --- EXIBIÇÃO FINAL ---
            resultado = df[(df['DISCIPLINA'] == sel_d) & 
                          (df['SERIE'] == sel_s) & 
                          (df['TURMA'] == sel_t)]
            
            st.subheader(f"✅ Resultados para: {sel_d} - {sel_s} {sel_t}")
            st.dataframe(resultado, use_container_width=True)
            
        else:
            st.error("⚠️ Não encontramos as colunas 'Disciplina' e 'Série'.")
            st.write("Colunas detectadas na linha de dados:", list(df.columns))
            st.info("Dica: Verifique se os nomes estão escritos corretamente na planilha.")

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
else:
    st.info("Aguardando o upload da planilha para liberar os filtros.")
