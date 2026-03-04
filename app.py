import streamlit as st
import pandas as pd

# 1. Configuração de Interface
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

# 2. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # Tenta ler a planilha pulando as linhas de instrução (ajustado para linha 3)
        df = pd.read_excel(uploaded_file, skiprows=2)
        
        # LIMPEZA TOTAL: Remove espaços, acentos e padroniza para MAIÚSCULO
        df.columns = [str(c).strip().upper()
                      .replace('É', 'E').replace('Í', 'I') 
                      for c in df.columns]

        # Mapeia as colunas necessárias
        mapa = {'SERIE': 'SERIE', 'DISCIPLINA': 'DISCIPLINA', 'TURMA': 'TURMA'}
        df.rename(columns=mapa, inplace=True)

        # Verifica se as colunas essenciais existem
        cols_alvo = ['DISCIPLINA', 'SERIE', 'TURMA']
        if all(c in df.columns for c in cols_alvo):
            
            # Limpa os dados das células
            for col in cols_alvo:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS ---
            st.sidebar.header("Filtros")
            
            d_list = sorted(df['DISCIPLINA'].unique())
            d_sel = st.sidebar.selectbox("Disciplina", d_list)

            s_list = sorted(df[df['DISCIPLINA'] == d_sel]['SERIE'].unique())
            s_sel = st.sidebar.selectbox("Série", s_list)

            t_list = sorted(df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel)]['TURMA'].unique())
            t_sel = st.sidebar.selectbox("Turma", t_list)

            # Exibição dos Dados
            final = df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel) & (df['TURMA'] == t_sel)]
            
            st.subheader(f"📊 Resultados: {d_sel} - {s_sel} {t_sel}")
            st.dataframe(final, use_container_width=True)
            
        else:
            # Caso o skiprows=2 não funcione, ele mostra o que leu para ajudar no ajuste
            st.error("⚠️ Não encontramos as colunas 'Disciplina', 'Série' e 'Turma'.")
            st.write("O sistema leu estas colunas na linha 3:", list(df.columns))
            st.info("Dica: Certifique-se de que os títulos das colunas estão exatamente na linha 3 da planilha.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Aguardando o upload da planilha para liberar o acesso das coordenadoras.")
