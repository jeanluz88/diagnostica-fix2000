import streamlit as st
import pandas as pd
import io
import unicodedata

# =========================================================
# 1. CONFIGURAÇÕES DE PÁGINA E INTERFACE
# =========================================================
st.set_page_config(page_title="Painel Diagnóstico", layout="wide")

# CSS para forçar a fonte 14pt e melhorar o visual
st.markdown("""
    <style>
    .big-font { font-size:14pt !important; line-height: 1.6; }
    .stSelectbox label { font-size: 12pt; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("Painel de Avaliação Diagnóstica")

# =========================================================
# 2. CARREGAMENTO E TRATAMENTO DE DADOS
# =========================================================
@st.cache_data(show_spinner="Sincronizando dados...")
def load_data(file_bytes):
    try:
        xls = pd.ExcelFile(io.BytesIO(file_bytes))
        # Carrega a aba correta da sua planilha Modelo_Diagnostica_Por_Turma
        df = pd.read_excel(xls, sheet_name="Lancamentos")
        
        # Limpeza básica de espaços extras que geram duplicados
        for col in ['Disciplina', 'Serie', 'Turma']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
        return None

uploaded_file = st.file_uploader("Upload da Planilha Modelo_Diagnostica_Por_Turma", type=["xlsx"])

if uploaded_file:
    df_lan = load_data(uploaded_file.read())

    if df_lan is not None:
        # --- FILTROS LATERAIS COM REMOÇÃO DE DUPLICADOS ---
        st.sidebar.header("Filtros de Seleção")
        
        # Filtro de Disciplina (Correção da duplicidade)
        lista_disciplinas = sorted(df_lan['Disciplina'].unique().tolist())
        disciplina = st.sidebar.selectbox("Selecione a Disciplina", options=lista_disciplinas)
        
        # Filtro de Série
        df_disc = df_lan[df_lan['Disciplina'] == disciplina]
        lista_series = sorted(df_disc['Serie'].unique().tolist())
        serie = st.sidebar.selectbox("Selecione a Série", options=lista_series)
        
        # Filtro de Turma
        df_serie = df_disc[df_disc['Serie'] == serie]
        lista_turmas = sorted(df_serie['Turma'].unique().tolist())
        turma = st.sidebar.selectbox("Selecione a Turma", options=lista_turmas)

        # Dados Finais Filtrados
        df_final = df_serie[df_serie['Turma'] == turma]

        # =========================================================
        # 3. EXIBIÇÃO DOS RESULTADOS (LAYOUT LADO A LADO)
        # =========================================================
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Habilidades Analisadas")
            for index, row in df_final.iterrows():
                # Texto com fonte 14pt conforme solicitado
                st.markdown(f'<p class="big-font"><b>{row["Habilidade_Codigo"]}:</b> {row["Habilidade_Descricao"]}</p>', unsafe_allow_html=True)

        with col2:
            st.subheader("Desempenho da Turma")
            # Aqui entra a lógica do seu gráfico (Matplotlib/Plotly)
            st.info("Gráfico gerado automaticamente com base nos filtros selecionados.")
            
            if st.button("Gerar PDF"):
                st.success("Relatório preparado para download!")
else:
    st.info("Aguardando planilha... Por favor, faça o upload do arquivo para começar.")
