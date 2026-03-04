import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

# 2. Upload do Arquivo
uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # LER A PLANILHA SEM CABEÇALHO PARA LOCALIZAR OS DADOS
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # Busca automática: encontra a linha que contém as palavras principais
        # Isso ignora as linhas de "Como usar" ou avisos do topo da planilha
        start_row = 0
        for i, row in df_raw.iterrows():
            linha_texto = " ".join([str(v).lower() for v in row.values])
            if 'disciplina' in linha_texto and 'serie' in linha_texto:
                start_row = i
                break
        
        # Relê a planilha a partir da linha correta
        df = pd.read_excel(uploaded_file, skiprows=start_row)
        
        # NORMALIZAÇÃO TOTAL DAS COLUNAS
        # Remove espaços, acentos e deixa tudo em MAIÚSCULO
        df.columns = [
            str(c).strip().upper()
            .replace('É', 'E').replace('Í', 'I').replace('Á', 'A') 
            for c in df.columns
        ]

        # Verifica se as colunas vitais foram encontradas
        cols_necessarias = ['DISCIPLINA', 'SERIE', 'TURMA']
        if all(c in df.columns for c in cols_necessarias):
            
            # Limpa espaços em branco dentro das células
            for col in cols_necessarias:
                df[col] = df[col].astype(str).str.strip()

            # --- SISTEMA DE FILTROS ---
            st.sidebar.header("Filtros de Seleção")
            
            d_list = sorted(df['DISCIPLINA'].unique())
            d_sel = st.sidebar.selectbox("Selecione a Disciplina", d_list)

            s_list = sorted(df[df['DISCIPLINA'] == d_sel]['SERIE'].unique())
            s_sel = st.sidebar.selectbox("Selecione a Série", s_list)

            t_list = sorted(df[(df['DISCIPLINA'] == d_sel) & (df['SERIE'] == s_sel)]['TURMA'].unique())
            t_sel = st.sidebar.selectbox("Selecione a Turma", t_list)

            # --- EXIBIÇÃO ---
            exibir = df[(df['DISCIPLINA'] == d_sel) & 
                        (df['SERIE'] == s_sel) & 
                        (df['TURMA'] == t_sel)]
            
            st.subheader(f"✅ Resultados encontrados para {d_sel}")
            st.dataframe(exibir, use_container_width=True)
            
        else:
            st.error("⚠️ Títulos não encontrados.")
            st.write("O sistema tentou ler a partir da linha", start_row + 1, "mas achou isto:", list(df.columns))
            st.info("Dica: Certifique-se de que 'Disciplina' e 'Série' estão escritos corretamente na sua planilha.")

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
else:
    st.info("Aguardando o upload da planilha para liberar os filtros.")
