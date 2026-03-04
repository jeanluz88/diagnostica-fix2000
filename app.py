# --- GRÁFICOS COM ALINHAMENTO E VISIBILIDADE CORRIGIDA ---
    # Calculamos a altura dinamicamente para não amassar as barras no site
    altura_dinamica = max(8, len(df_agg) * 0.9) 
    fig, ax = plt.subplots(figsize=(16, altura_dinamica))
    
    # Cores fixas do padrão semáforo
    ax.barh(df_agg["Label"], df_agg["p_sim"], color="#2ecc71", label="SIM")
    ax.barh(df_agg["Label"], df_agg["p_par"], left=df_agg["p_sim"], color="#f1c40f", label="PARCIAL")
    ax.barh(df_agg["Label"], df_agg["p_nao"], left=df_agg["p_sim"]+df_agg["p_par"], color="#e74c3c", label="NÃO")

    # AJUSTE DE FONTE E ALINHAMENTO PARA O SITE
    # 'ha=right' garante que o texto longo não sobreponha as barras
    ax.set_yticklabels(df_agg["Label"], fontweight='bold', fontsize=12, ha='right')

    # ESTA LINHA É A CHAVE: Ajusta as margens para o texto caber na esquerda
    # left=0.4 significa que 40% da largura será reservada para o texto da habilidade
    plt.subplots_adjust(left=0.4, right=0.95, top=0.95, bottom=0.1) 

    # Inserção das porcentagens e valores dentro das barras
    for i in range(len(df_agg)):
        s, p, n = int(df_agg["SIM"].iloc[i]), int(df_agg["PARCIAL"].iloc[i]), int(df_agg["NÃO"].iloc[i])
        ps, pp, pn = df_agg["p_sim"].iloc[i], df_agg["p_par"].iloc[i], df_agg["p_nao"].iloc[i]
        
        # Só escreve se houver espaço (p_sim > 5%) para não embolar o texto
        if ps > 5:
            ax.text(ps/2, i, f"{s}\n({ps:.0f}%)", va='center', ha='center', color='white', fontweight='bold', fontsize=10)
        if pp > 5:
            ax.text(ps + pp/2, i, f"{p}\n({pp:.0f}%)", va='center', ha='center', color='black', fontweight='bold', fontsize=10)
        if pn > 5:
            ax.text(ps + pp + pn/2, i, f"{n}\n({pn:.0f}%)", va='center', ha='center', color='white', fontweight='bold', fontsize=10)

    ax.set_xlim(0, 100)
    ax.set_xlabel("Porcentagem de Aproveitamento (%)", fontsize=12, fontweight='bold')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=12, frameon=False)
    
    # Limpeza visual
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.xaxis.grid(color='gray', linestyle='--', alpha=0.3) # Linhas de grade para facilitar leitura

    # EXIBIÇÃO NO STREAMLIT COM DPI ALTO PARA NITIDEZ
    st.pyplot(fig, use_container_width=True)
