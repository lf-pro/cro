import streamlit as st
import pandas as pd
from scripts import run_bootstrap
from scripts import run_bayes_scipy
from scripts import run_bayes_beta

st.set_page_config(page_title="Análise de Teste A/B", layout="wide")

st.title("Plataforma de Análise de Teste A/B")
st.caption("Developed by LF Corporations")

uploaded_file = st.file_uploader("Envie o arquivo Excel com colunas: data, variante, receita, sessoes")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.sidebar.markdown("### Escolha as análises que deseja rodar:")
    bootstrap_selected = st.sidebar.checkbox("Bootstrapping Diário")
    bayes_scipy_selected = st.sidebar.checkbox("Bayesiano com Beta (RPV Escalado)")
    bayes_beta_selected = st.sidebar.checkbox("Bayesiano")

    if bootstrap_selected:
        st.subheader("Resultado Bootstrapping Diário")
        run_bootstrap.run_bootstrap(df)
        st.markdown("""
        🔍 **O que foi feito?** A análise de bootstrapping calcula a média da receita por visita (RPV) para cada grupo
        com simulações aleatórias para gerar um intervalo de confiança de 90%.

        ✅ Indica se a nova variante tem desempenho superior, inferior ou se o resultado é inconclusivo.
        """)

    if bayes_scipy_selected:
        st.subheader("Resultado Bayesiano com Beta (RPV Escalado)")
        run_bayes_scipy.run_bayes_scipy(df)
        st.markdown("""
        🔍 **O que foi feito?** Usamos uma distribuição Beta para modelar a incerteza sobre a receita por visita (RPV),
        escalando os valores para ficarem entre 0 e 1.

        📈 Foram geradas distribuições para cada variante, e a probabilidade da nova variante ser melhor foi calculada.
        """)

    if bayes_beta_selected:
        st.subheader("Resultado Bayesiano")
        run_bayes_beta.run_bayes_beta(df)
        st.markdown("""
        🔍 **O que foi feito?** Uma abordagem bayesiana foi aplicada diretamente sobre os dados de RPV, sem escalonamento,
        considerando a média e variação dos grupos.

        📊 O resultado mostra o quanto a nova variante é melhor (ou pior) do que o controle com base em inferência estatística.
        """)

    if not any([bootstrap_selected, bayes_scipy_selected, bayes_beta_selected]):
        st.info("Selecione ao menos uma análise no menu lateral para visualizar os resultados.")
