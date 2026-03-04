import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel Diagnóstico", layout="wide")
st.title("📊 Painel de Avaliação Diagnóstica")

uploaded_file = st.file_uploader("Arraste a planilha NAVARRO.xlsx aqui", type=["xlsx"])

if uploaded_file:
    try:
        # 1. Carregar especificamente a aba de 'Lancamentos'
        # Usamos engine='openpyxl' para garantir compatibilidade
        df = pd.read_excel(uploaded_file, sheet_name='Lancamentos')
        
        # 2. Padronização Radical de Colunas
        # Remove espaços, acentos e caracteres especiais para evitar erros de busca
        df.columns = [
            str(c).strip().upper()
            .replace('Á', 'A').replace('É', 'E').replace('Í', 'I')
            .replace('Ó', 'O').replace('Ú', 'U')
            .replace('/', '_').replace(' ', '_')
            for c in df.columns
        ]

        # 3. Mapeamento Inteligente
        # A coluna na planilha é 'ANO/SÉRIE', no código tratamos como 'ANO_SERIE'
        mapeamento = {
            'ANO_SERIE': 'SERIE',
            'DISCIPLINA': 'DISCIPLINA',
            'TURMA': 'TURMA'
        }
        df.rename(columns=mapeamento, inplace=True)

        # 4. Verificação de Colunas Vitais
        colunas_necessarias = ['DISCIPLINA', 'SERIE', 'TURMA']
        
        if all(c in df.columns for c in colunas_necessarias):
            # Limpeza de dados das células
            for col in colunas_necessarias:
                df[col] = df[col].astype(str).str.strip()

            # --- INTERFACE DE FILTROS ---
            st.sidebar.header("Filtros de Avaliação")
            
            # Disciplina
            lista_disc = sorted(df['DISCIPLINA'].unique())
            sel_disc = st.sidebar.selectbox("Escolha a Disciplina", lista_disc)

            # Série (filtrada por disciplina)
            df_filt_disc = df[df['DISCIPLINA'] == sel_disc]
            lista_serie = sorted(df_filt_disc['SERIE'].unique())
            sel_serie = st.sidebar.selectbox("Escolha a Série", lista_serie)

            # Turma (filtrada por série e disciplina)
            df_filt_serie = df_filt_disc[df_filt_disc['SERIE'] == sel_serie]
            lista_turma = sorted(df_filt_serie['TURMA'].unique())
            sel_turma = st.sidebar.selectbox("Escolha a Turma", lista_turma)

            # --- EXIBIÇÃO ---
            df_final = df_filt_serie[df_filt_serie['TURMA'] == sel_turma]
            
            st.subheader(f"✅ Dados Filtrados: {sel_disc} | {sel_serie} - Turma {sel_turma}")
            
            if not df_final.empty:
                # Exibe a tabela com as colunas principais
                colunas_exibir = ['HABILIDADE', 'TOTAL_DE_ALUNOS', 'SIM', 'PARCIAL', 'NAO']
                # Verifica se essas colunas de dados existem antes de exibir
                cols_presentes = [c for c in colunas_exibir if c in df_final.columns]
                
                st.dataframe(df_final[cols_presentes + ['QUESTAO_ITEM']], use_container_width=True)
            else:
                st.warning("Nenhum dado encontrado para os filtros selecionados.")
        
        else:
            st.error("⚠️ Erro na estrutura da planilha.")
            st.write("Colunas detectadas:", list(df.columns))
            st.info("A aba 'Lancamentos' deve conter as colunas: Ano/Série, Disciplina e Turma.")

    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
else:
    st.info("Aguardando upload do arquivo para processar os dados das coordenadoras.")
