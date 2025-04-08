import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def run_metrics_analysis(data):
    """
    Executa análise de métricas básicas:
    - Receita por Sessão (RPS)
    - Receita Total por Variante
    - Sessões Totais por Variante
    - Conversão implícita (se receita > 0 for conversão)
    - Sample Ratio Mismatch (SRM)
    """
    # Configuração de estilo para os gráficos
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Verificar se os dados contêm as colunas necessárias
    required_columns = ['data', 'variante', 'receita', 'sessoes']
    if not all(col in data.columns for col in required_columns):
        st.error("Dados não contêm todas as colunas necessárias: data, variante, receita, sessoes")
        return
    
    # Calcular Sample Ratio Mismatch (SRM)
    st.subheader("🔄 Sample Ratio Mismatch (SRM)")
    
    # Contagem de sessões por variante
    variant_counts = data.groupby('variante')['sessoes'].sum()
    
    # Verificar se temos exatamente duas variantes
    if len(variant_counts) == 2:
        variants = variant_counts.index.tolist()
        expected_ratio = 0.5  # Esperamos uma divisão 50/50 entre controle e variante
        
        # Calcular proporção observada
        total_sessions = variant_counts.sum()
        observed_ratio = variant_counts[variants[1]] / total_sessions
        
        # Calcular p-valor para o teste binomial
        from scipy import stats
        try:
            # Para versões mais recentes do SciPy
            p_value = stats.binomtest(
                k=int(variant_counts[variants[1]]), 
                n=int(total_sessions), 
                p=expected_ratio
            ).pvalue
        except AttributeError:
            # Fallback para versões mais antigas do SciPy
            p_value = stats.binom_test(
                int(variant_counts[variants[1]]), 
                n=int(total_sessions), 
                p=expected_ratio
            )
        
        # Exibir resultados
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Proporção Esperada", f"{expected_ratio:.1%}")
            st.metric("Proporção Observada", f"{observed_ratio:.1%}")
            st.metric("Diferença", f"{(observed_ratio - expected_ratio) * 100:.2f}pp")
        
        with col2:
            st.metric("P-valor", f"{p_value:.4f}")
            
            # Interpretação do SRM
            if p_value < 0.05:
                st.error("⚠️ **SRM Detectado!** A distribuição de tráfego entre as variantes não é aleatória (p < 0.05).")
                st.warning("Os resultados do teste podem estar comprometidos devido à alocação desigual de tráfego.")
            else:
                st.success("✅ **SRM Não Detectado.** A distribuição de tráfego entre as variantes parece aleatória (p ≥ 0.05).")
                st.info("A alocação de tráfego está dentro do esperado para um teste A/B válido.")
    else:
        st.warning("O cálculo de SRM requer exatamente duas variantes (Controle e Variante).")
    
    st.markdown("---")
    
    # Calcular métricas por variante
    metrics = data.groupby('variante').agg(
        receita_total=('receita', 'sum'),
        sessoes_total=('sessoes', 'sum')
    ).reset_index()
    
    # Calcular RPS (Receita por Sessão)
    metrics['rps'] = metrics['receita_total'] / metrics['sessoes_total']
    
    # Calcular conversão implícita (se receita > 0)
    conversao = data.copy()
    conversao['converteu'] = (conversao['receita'] > 0).astype(int)
    conv_metrics = conversao.groupby('variante').agg(
        conversoes=('converteu', 'sum'),
        sessoes_total=('sessoes', 'sum')
    ).reset_index()
    conv_metrics['taxa_conversao'] = (conv_metrics['conversoes'] / conv_metrics['sessoes_total']) * 100
    
    # Exibir métricas em tabelas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Métricas Gerais")
        st.dataframe(metrics)
        
        # Calcular diferença percentual entre variantes
        if len(metrics) == 2:
            control = metrics[metrics['variante'] == 'Controle']
            variant = metrics[metrics['variante'] != 'Controle']
            
            if not control.empty and not variant.empty:
                rps_diff = ((variant['rps'].values[0] / control['rps'].values[0]) - 1) * 100
                receita_diff = ((variant['receita_total'].values[0] / control['receita_total'].values[0]) - 1) * 100
                sessoes_diff = ((variant['sessoes_total'].values[0] / control['sessoes_total'].values[0]) - 1) * 100
                
                st.info(f"Diferença na RPS: {rps_diff:.2f}%")
                st.info(f"Diferença na Receita Total: {receita_diff:.2f}%")
                st.info(f"Diferença nas Sessões: {sessoes_diff:.2f}%")
    
    with col2:
        st.subheader("🔄 Taxas de Conversão")
        st.dataframe(conv_metrics[['variante', 'conversoes', 'taxa_conversao']])
        
        # Calcular diferença percentual na conversão
        if len(conv_metrics) == 2:
            control = conv_metrics[conv_metrics['variante'] == 'Controle']
            variant = conv_metrics[conv_metrics['variante'] != 'Controle']
            
            if not control.empty and not variant.empty:
                conv_diff = ((variant['taxa_conversao'].values[0] / control['taxa_conversao'].values[0]) - 1) * 100
                st.info(f"Diferença na Taxa de Conversão: {conv_diff:.2f}%")
    
    # Visualizações
    st.subheader("📈 Visualizações")
    
    # Gráfico de barras para RPS
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='variante', y='rps', data=metrics, palette=['#1E88E5', '#00e13a'], ax=ax1)
    ax1.set_title('Receita por Sessão (RPS) por Variante')
    ax1.set_ylabel('RPS')
    ax1.set_xlabel('Variante')
    st.pyplot(fig1)
    
    # Gráfico de barras para taxa de conversão
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='variante', y='taxa_conversao', data=conv_metrics, palette=['#1E88E5', '#00e13a'], ax=ax2)
    ax2.set_title('Taxa de Conversão por Variante (%)')
    ax2.set_ylabel('Taxa de Conversão (%)')
    ax2.set_xlabel('Variante')
    st.pyplot(fig2)
    
    # Análise diária
    st.subheader("📅 Análise Diária")
    
    # Calcular métricas diárias
    daily_metrics = data.groupby(['data', 'variante']).agg(
        receita_diaria=('receita', 'sum'),
        sessoes_diarias=('sessoes', 'sum')
    ).reset_index()
    daily_metrics['rps_diario'] = daily_metrics['receita_diaria'] / daily_metrics['sessoes_diarias']
    
    # Gráfico de linha para RPS diário
    fig5, ax5 = plt.subplots(figsize=(12, 6))
    for variante, grupo in daily_metrics.groupby('variante'):
        ax5.plot(grupo['data'], grupo['rps_diario'], marker='o', label=variante)
    ax5.set_title('Evolução Diária da RPS por Variante')
    ax5.set_ylabel('RPS')
    ax5.set_xlabel('Data')
    ax5.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig5)
    
    # Conclusão
    st.subheader("🔍 Conclusão")
    
    if len(metrics) == 2:
        control = metrics[metrics['variante'] == 'Controle']
        variant = metrics[metrics['variante'] != 'Controle']
        
        if not control.empty and not variant.empty:
            if rps_diff > 0:
                st.success(f"✅ A variante apresenta uma RPS {rps_diff:.2f}% maior que o controle.")
            else:
                st.error(f"❌ A variante apresenta uma RPS {abs(rps_diff):.2f}% menor que o controle.")
            
            if conv_diff > 0:
                st.success(f"✅ A taxa de conversão da variante é {conv_diff:.2f}% maior que o controle.")
            else:
                st.error(f"❌ A taxa de conversão da variante é {abs(conv_diff):.2f}% menor que o controle.")


