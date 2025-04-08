# scripts/__init__.py (arquivo vazio apenas para reconhecer como pacote Python)

# scripts/run_bootstrap.py
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

def run_bootstrap(df):
    df["data"] = pd.to_datetime(df["data"])
    df["rpv"] = df["receita"] / df["sessoes"]
    rpv_diario = df.groupby(["data", "variante"]).agg({"rpv": "mean"}).reset_index()

    controle = rpv_diario[rpv_diario["variante"] == "Controle"]["rpv"].values
    nova = rpv_diario[rpv_diario["variante"] == "Nova"]["rpv"].values

    def bootstrap(data, num_samples=10000):
        boot_means = [np.mean(np.random.choice(data, size=len(data), replace=True)) for _ in range(num_samples)]
        return np.percentile(boot_means, [5, 95]), np.array(boot_means)

    ci_controle, boot_controle = bootstrap(controle)
    ci_nova, boot_nova = bootstrap(nova)

    diff_boot = boot_nova - boot_controle
    ci_diff = np.percentile(diff_boot, [5, 95])
    p_value = (diff_boot < 0).mean()

    # Reposicionamento dos dados ao lado dos gráficos
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de distribuição
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        sns.histplot(boot_controle, bins=50, color='#3498db', alpha=0.6, label='Controle', kde=True)
        sns.histplot(boot_nova, bins=50, color='#2ecc71', alpha=0.6, label='Nova', kde=True)
        ax.axvline(ci_controle[0], color='#3498db', linestyle='dashed', linewidth=1.5)
        ax.axvline(ci_controle[1], color='#3498db', linestyle='dashed', linewidth=1.5)
        ax.axvline(ci_nova[0], color='#2ecc71', linestyle='dashed', linewidth=1.5)
        ax.axvline(ci_nova[1], color='#2ecc71', linestyle='dashed', linewidth=1.5)
        ax.legend(frameon=True, fancybox=True, shadow=True)
        ax.set_title("Distribuição do RPV Diário com Intervalos de Confiança", fontweight='bold')
        ax.set_xlabel("Receita por Visita (RPV)")
        ax.set_ylabel("Frequência")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Dados estatísticos
        st.markdown("### Resultados Estatísticos")
        st.write(f"**RPV Controle:**")
        st.write(f"Média = {np.mean(controle):.4f}")
        st.write(f"IC 90% = [{ci_controle[0]:.4f}, {ci_controle[1]:.4f}]")
        
        st.write(f"**RPV Nova:**")
        st.write(f"Média = {np.mean(nova):.4f}")
        st.write(f"IC 90% = [{ci_nova[0]:.4f}, {ci_nova[1]:.4f}]")
        
        st.write(f"**Diferença:**")
        st.write(f"Média = {np.mean(diff_boot):.4f}")
        st.write(f"IC 90% = [{ci_diff[0]:.4f}, {ci_diff[1]:.4f}]")
        
        st.write(f"**p-valor** (Nova pior ou igual ao Controle): {p_value:.4f}")
        
        # Interpretação do resultado
        if ci_diff[0] > 0:
            st.success("✅ Nova variante é estatisticamente superior (90% de confiança)")
        elif ci_diff[1] < 0:
            st.error("❌ Nova variante é estatisticamente inferior (90% de confiança)")
        else:
            st.warning("⚠️ Resultado inconclusivo (90% de confiança)")

    # Segundo gráfico (diferença) com dados ao lado
    col3, col4 = st.columns([2, 1])
    
    with col3:
        fig2, ax2 = plt.subplots(figsize=(10, 5), dpi=150)
        sns.histplot(diff_boot, bins=50, color='#9b59b6', alpha=0.7, kde=True)
        ax2.axvline(ci_diff[0], color='#e74c3c', linestyle='dashed', linewidth=1.5)
        ax2.axvline(ci_diff[1], color='#e74c3c', linestyle='dashed', linewidth=1.5)
        ax2.axvline(0, color='black', linestyle='solid', linewidth=1.5)
        ax2.set_title("Diferença entre Nova e Controle (RPV Diário)", fontweight='bold')
        ax2.set_xlabel("Diferença de RPV")
        ax2.set_ylabel("Frequência")
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)
    
    with col4:
        # Interpretação da diferença
        st.markdown("### Interpretação da Diferença")
        
        lift = (np.mean(nova) / np.mean(controle) - 1) * 100
        st.metric("Lift", f"{lift:.2f}%", delta=f"{lift:.2f}%")
        
        if p_value < 0.05:
            st.success(f"Probabilidade da Nova ser melhor: {(1-p_value)*100:.1f}%")
        elif p_value < 0.1:
            st.warning(f"Probabilidade da Nova ser melhor: {(1-p_value)*100:.1f}%")
        else:
            st.error(f"Probabilidade da Nova ser melhor: {(1-p_value)*100:.1f}%")
        
        # Recomendação
        st.markdown("### Recomendação")
        if p_value < 0.05:
            st.success("Implementar a Nova variante")
        elif p_value < 0.1:
            st.warning("Considerar mais testes")
        else:
            st.error("Manter a variante Controle")
