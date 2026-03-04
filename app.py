import streamlit as st
import pandas as pd

# 1. Configuração de Página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

# 2. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # Pula as 2 primeiras linhas que costumam ser títulos mesclados em planilhas escolares
        df = pd.read_excel(uploaded_file, skiprows=2)
        
        # Limpa nomes das colunas (remove espaços e acentos)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Mapeia os nomes das colunas para o sistema entender
        mapeamento = {
            'SÉRIE': 'SERIE', 'DISCIPLINA': 'DISCIPLINA', 
            'TURMA': 'TURMA', 'HABILIDADE': 'HABILIDADE'
        }
        df.rename(columns=mapeamento, inplace=True)

        # Verifica se as colunas principais foram encontradas
        colunas_necessarias = ['DISCIPLINA', 'SERIE', 'TURMA']
        if all(c in df.columns for c in colunas_necessarias):
            
            # Limpa espaços em branco dentro das células
            for col in colunas_necessarias:
                df[col] = df[col].astype(str).str.strip()

            # --- FILTROS ÚNICOS ---
            st.sidebar.header("Filtros")
            disciplinas = sorted(df['DISCIPLINA'].unique())
            disc_sel = st.sidebar.selectbox("Escolha a Disciplina", disciplinas)

            series = sorted(df[df['DISCIPLINA'] == disc_sel]['SERIE'].unique())
            serie_sel = st.sidebar.selectbox("Escolha a Série", series)

            turmas = sorted(df[(df['DISCIPLINA'] == disc_sel) & (df['SERIE'] == serie_sel)]['TURMA'].unique())
            turma_sel = st.sidebar.selectbox("Escolha a Turma", turmas)

            # --- RESULTADO FINAL ---
            dados_filtrados = df[(df['DISCIPLINA'] == disc_sel) & 
                                 (df['SERIE'] == serie_sel) & 
                                 (df['TURMA'] == turma_sel)]

            st.subheader(f"📊 Dados de {disc_sel} - {serie_sel} {turma_sel}")
            st.dataframe(dados_filtrados, use_container_width=True)
            
        else:
            st.error("⚠️ Formato de planilha não reconhecido.")
            st.write("Colunas encontradas após o ajuste:", list(df.columns))
            st.info("Verifique se as colunas Disciplina, Série e Turma estão na linha 3 da sua planilha.")

    except Exception as e:
        st.error(f"Erro técnico: {e}")
else:
    st.info("Aguardando o upload da planilha para liberar os filtros das coordenadoras.")
