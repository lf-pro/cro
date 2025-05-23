# scripts/__init__.py (arquivo vazio apenas para reconhecer como pacote Python)

# scripts/run_bootstrap.py
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

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

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.histplot(diff_boot, bins=50, color='purple', alpha=0.7)
    ax2.axvline(ci_diff[0], color='red', linestyle='dashed')
    ax2.axvline(ci_diff[1], color='red', linestyle='dashed')
    ax2.axvline(0, color='black', linestyle='solid')
    ax2.set_title("Diferença entre Nova e Controle (RPV Diário)")
    st.pyplot(fig2)

    st.markdown("---")
    st.write(f"**RPV Controle**: Média = {np.mean(controle):.4f}, IC 90% = {ci_controle}")
    st.write(f"**RPV Nova**: Média = {np.mean(nova):.4f}, IC 90% = {ci_nova}")
    st.write(f"**Diferença**: Média = {np.mean(diff_boot):.4f}, IC 90% = {ci_diff}")
    st.write(f"**p-valor** (Nova pior ou igual ao Controle): {p_value:.4f}")

    if ci_diff[0] > 0:
        st.success("✅ A nova variante superou significativamente a versão Controle!")
    elif ci_diff[1] < 0:
        st.error("❌ A nova variante teve desempenho inferior ao Controle!")
    else:
        st.warning("⚠️ O teste não teve um resultado estatisticamente significativo. Mais dados podem ser necessários.")


# scripts/run_bayes_scipy.py (renomeado de run_bayes_beta)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import beta
import streamlit as st

def run_bayes_scipy(df):
    df["data"] = pd.to_datetime(df["data"])
    df["rpv"] = df["receita"] / df["sessoes"]
    rpv_diario = df.groupby(["data", "variante"]).agg({"rpv": "mean"}).reset_index()

    controle = rpv_diario[rpv_diario["variante"] == "Controle"]["rpv"].values
    nova = rpv_diario[rpv_diario["variante"] == "Nova"]["rpv"].values

    min_rpv = min(np.min(controle), np.min(nova))
    max_rpv = max(np.max(controle), np.max(nova))
    controle_scaled = (controle - min_rpv) / (max_rpv - min_rpv)
    nova_scaled = (nova - min_rpv) / (max_rpv - min_rpv)

    alpha_prior, beta_prior = 2, 2
    alpha_controle = alpha_prior + np.sum(controle_scaled)
    beta_controle = beta_prior + len(controle_scaled) - np.sum(controle_scaled)
    alpha_nova = alpha_prior + np.sum(nova_scaled)
    beta_nova = beta_prior + len(nova_scaled) - np.sum(nova_scaled)

    samples_controle = beta.rvs(alpha_controle, beta_controle, size=10000)
    samples_nova = beta.rvs(alpha_nova, beta_nova, size=10000)

    prob_nova_melhor = (samples_nova > samples_controle).mean()

    # Reposicionamento dos dados ao lado dos gráficos
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de distribuição
        fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
        sns.kdeplot(samples_controle, label='Controle', color='#3498db', fill=True, alpha=0.6, linewidth=2)
        sns.kdeplot(samples_nova, label='Nova', color='#2ecc71', fill=True, alpha=0.6, linewidth=2)
        ax.axvline(np.percentile(samples_controle, 5), color='#3498db', linestyle='dashed', linewidth=1.5)
        ax.axvline(np.percentile(samples_controle, 95), color='#3498db', linestyle='dashed', linewidth=1.5)
        ax.axvline(np.percentile(samples_nova, 5), color='#2ecc71', linestyle='dashed', linewidth=1.5)
        ax.axvline(np.percentile(samples_nova, 95), color='#2ecc71', linestyle='dashed', linewidth=1.5)
        ax.set_title("Distribuição Bayesiana do RPV", fontweight='bold')
        ax.set_xlabel("Receita por Visita (RPV)")
        ax.set_ylabel("Densidade")
        ax.legend(frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Dados estatísticos
        st.markdown("### Resultados Bayesianos")
        st.write(f"**RPV Controle:**")
        st.write(f"Média = {np.mean(samples_controle):.4f}")
        st.write(f"IC 90% = [{np.percentile(samples_controle, 5):.4f}, {np.percentile(samples_controle, 95):.4f}]")
        
        st.write(f"**RPV Nova:**")
        st.write(f"Média = {np.mean(samples_nova):.4f}")
        st.write(f"IC 90% = [{np.percentile(samples_nova, 5):.4f}, {np.percentile(samples_nova, 95):.4f}]")
        
        # Probabilidade e interpretação
        st.markdown("### Probabilidade")
        st.metric("Nova > Controle", f"{prob_nova_melhor:.2%}")
        
        # Interpretação do resultado
        st.markdown("### Interpretação")
        if prob_nova_melhor > 0.95:
            st.success("✅ Nova variante é superior (95% de certeza)")
        elif prob_nova_melhor > 0.90:
            st.success("✅ Nova variante é provavelmente superior (90% de certeza)")
        elif prob_nova_melhor < 0.05:
            st.error("❌ Nova variante é inferior (95% de certeza)")
        elif prob_nova_melhor < 0.10:
            st.error("❌ Nova variante é provavelmente inferior (90% de certeza)")
        else:
            st.warning("⚠️ Resultado inconclusivo")
