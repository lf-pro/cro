import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scripts import run_bootstrap, run_bayes_scipy, run_bayes_beta, run_metrics_analysis

# Configuração da página
st.set_page_config(
    page_title="Experimentos A/B",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar tema na sessão se não existir
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Configuração global para melhorar a qualidade dos gráficos
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16
plt.style.use('seaborn-v0_8-whitegrid')

# Função para alternar tema
def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
    st.rerun()

# Aplicar CSS baseado no tema
if st.session_state.theme == 'dark':
    # Tema escuro (padrão)
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #00e13a;
            text-align: center;
        }
        .sub-header {
            font-size: 1.8rem;
            color: #0D47A1;
            padding-top: 1rem;
        }
        .method-card {
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }
        .sidebar-header {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .stButton>button {
            width: 100%;
            margin-bottom: 10px;
            background-color: #00e13a;
            color: white;
        }
        .stButton>button:hover {
            background-color: #00c133;
            color: white;
        }
        .stButton>button:active {
            background-color: #00a52b;
            color: white;
        }
        .stButton>button:focus {
            box-shadow: 0 0 0 0.2rem rgba(0, 225, 58, 0.5);
        }
        .home-button {
            background-color: #00e13a !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # Tema claro
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #008f24;
            text-align: center;
        }
        .sub-header {
            font-size: 1.8rem;
            color: #1976D2;
            padding-top: 1rem;
        }
        .method-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .sidebar-header {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
        }
        .stButton>button {
            width: 100%;
            margin-bottom: 10px;
            background-color: #008f24;
            color: #ffffff;
        }
        .stButton>button:hover {
            background-color: #007a1f;
            color: #ffffff;
        }
        .stButton>button:active {
            background-color: #006519;
            color: #ffffff;
        }
        .stButton>button:focus {
            box-shadow: 0 0 0 0.2rem rgba(0, 143, 36, 0.5);
        }
        .home-button {
            background-color: #008f24 !important;
        }
        /* Ajustes específicos para tema claro */
        .stApp {
            background-color: #ffffff;
        }
        .stMarkdown {
            color: #333333;
        }
        .stExpander {
            border: 1px solid #e6e6e6;
            border-radius: 5px;
        }
        .stDataFrame {
            border: 1px solid #e6e6e6;
        }
        /* Ajustes adicionais para garantir legibilidade no tema claro */
        .stAlert p {
            color: #333333;
        }
        .stAlert a {
            color: #0056b3;
        }
        .stSelectbox label, .stSlider label, .stCheckbox label {
            color: #333333;
        }
        .stFileUploader label {
            color: #333333;
        }
        .stTextInput label {
            color: #333333;
        }
        /* Garantir que textos em botões permaneçam brancos */
        .stButton>button span {
            color: #ffffff !important;
        }
        /* Ajustar cores de texto em expanders */
        .streamlit-expanderHeader {
            color: #333333;
        }
        .streamlit-expanderContent {
            color: #333333;
        }
    </style>
    """, unsafe_allow_html=True)

# Inicializar estado da sessão se não existir
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'data' not in st.session_state:
    st.session_state.data = None

# Funções para navegação
def go_to_home():
    st.session_state.page = 'home'

def go_to_bootstrap():
    st.session_state.page = 'bootstrap'

def go_to_bayes_scipy():
    st.session_state.page = 'bayes_scipy'

def go_to_bayes_beta():
    st.session_state.page = 'bayes_beta'

def go_to_metrics_analysis():
    st.session_state.page = 'metrics_analysis'

# Cabeçalho principal
st.markdown('<div class="main-header">Análises de Experimentos A/B</div>', unsafe_allow_html=True)
st.caption("Developed by LF Corporations")

# Barra lateral com navegação
st.sidebar.markdown('<div class="sidebar-header"></div>', unsafe_allow_html=True)

# Seletor de tema
# theme_label = "🌙 Tema Escuro" if st.session_state.theme == 'dark' else "☀️ Tema Claro"
#if st.sidebar.button(theme_label, help="Alternar entre tema claro e escuro"):
    #toggle_theme()

# Botão Home sempre visível
if st.sidebar.button("🏠 Home", key="home_btn", help="Voltar para a página inicial"):
    go_to_home()

# Menu de análises sempre visível, mas botões desabilitados se não houver dados
st.sidebar.markdown('<div class="sidebar-header">🧪 Escolha uma análise:</div>', unsafe_allow_html=True)

# Verifica se há dados carregados
dados_carregados = st.session_state.data is not None

# Botões de análise (desabilitados se não houver dados)
if st.sidebar.button("📈 Bootstrapping Diário", key="bootstrap_btn", 
                    disabled=not dados_carregados,
                    help="Carregue dados primeiro" if not dados_carregados else "Análise com bootstrapping"):
    go_to_bootstrap()
    
if st.sidebar.button("📉 Bayesiano com Beta (RPV Escalado)", key="bayes_scipy_btn", 
                    disabled=not dados_carregados,
                    help="Carregue dados primeiro" if not dados_carregados else "Análise bayesiana com escalonamento"):
    go_to_bayes_scipy()
    
if st.sidebar.button("🧮 Bayesiano", key="bayes_beta_btn", 
                    disabled=not dados_carregados,
                    help="Carregue dados primeiro" if not dados_carregados else "Análise bayesiana simples"):
    go_to_bayes_beta()

if st.sidebar.button("📊 Métricas Básicas", key="metrics_btn", 
                    disabled=not dados_carregados,
                    help="Carregue dados primeiro" if not dados_carregados else "Análise de métricas básicas"):
    go_to_metrics_analysis()

# Adicionar mensagem informativa quando não houver dados
if not dados_carregados:
    st.sidebar.info("⚠️ Faça upload de dados na página inicial para habilitar as análises")

# Página Home
if st.session_state.page == 'home':
    # Instruções
    with st.expander("ℹ️ Como usar esta ferramenta", expanded=False):
        st.markdown("""
        1. Faça upload de um arquivo Excel contendo as colunas: `data`, `variante`, `receita`, `sessoes`
        2. Selecione um método de análise no menu lateral
        3. Visualize os resultados e interpretações para o método escolhido
        
        **Formato esperado do arquivo:**
        - `data`: Data da observação (AAAA-MM-DD)
        - `variante`: Nome da variante ("Controle" ou "Nova")
        - `receita`: Valor da receita gerada (Apenas números)
        - `sessoes`: Número de sessões/visitas
        """)

    # Upload de arquivo
    uploaded_file = st.file_uploader("📂 Envie o arquivo Excel com colunas: data, variante, receita, sessoes", 
                                    type=["xlsx", "xls"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.session_state.data = df
        
        # Exibir preview dos dados
        st.markdown('<div class="sub-header">🔍 Preview dos dados carregados</div>', unsafe_allow_html=True)
        st.dataframe(df.head(10), height=300)
        st.info(f"Total de {len(df)} registros carregados.")
        
        # Instruções para continuar
        st.success("✅ Dados carregados com sucesso! Selecione um método de análise no menu lateral.")
        
        # Força o rerun da aplicação para atualizar os botões na sidebar
        st.rerun()

# Página Bootstrapping
elif st.session_state.page == 'bootstrap':
    st.markdown('<div class="sub-header">📊 Resultado Bootstrapping Diário</div>', unsafe_allow_html=True)
    
    # Expander logo após o título
    with st.expander("ℹ️ Como o cálculo foi feito", expanded=False):
        st.markdown("""
        ### Metodologia de Bootstrapping Diário
        
        1. **Cálculo do RPV**: Para cada dia e variante, calculamos a Receita Por Visita (RPV = receita / sessões)
        
        2. **Bootstrapping**: Realizamos 10.000 reamostragens com reposição dos valores diários de RPV para cada variante
        
        3. **Intervalos de Confiança**: Calculamos o intervalo de confiança de 90% para a média do RPV de cada variante
        
        4. **Diferença**: Calculamos a diferença entre as médias de RPV das variantes em cada amostra bootstrap
        
        5. **P-valor**: Estimamos o p-valor como a proporção de amostras onde a diferença é menor que zero
        
        6. **Lift**: Calculamos o lift percentual como (RPV_nova / RPV_controle - 1) * 100
        
        Esta abordagem é robusta a outliers e não assume normalidade dos dados, sendo ideal para análises de testes A/B com dados diários.
        """)
    
    # Conteúdo da análise
    with st.container():
        run_bootstrap(st.session_state.data)
        
        st.markdown("""
        🔍 **O que foi feito?** A análise de bootstrapping calcula a média da receita por visita (RPV) para cada grupo
        com simulações aleatórias para gerar um intervalo de confiança de 90%.

        ✅ Indica se a nova variante tem desempenho superior, inferior ou se o resultado é inconclusivo.
        """)

# Página Bayes Scipy
elif st.session_state.page == 'bayes_scipy':
    st.markdown('<div class="sub-header">📊 Resultado Bayesiano com Beta (RPV Escalado)</div>', unsafe_allow_html=True)
    
    # Expander logo após o título
    with st.expander("ℹ️ Como o cálculo foi feito", expanded=False):
        st.markdown("""
        ### Metodologia Bayesiana com Distribuição Beta (RPV Escalado)
        
        1. **Cálculo do RPV**: Para cada dia e variante, calculamos a Receita Por Visita (RPV = receita / sessões)
        
        2. **Normalização**: Escalamos os valores de RPV para o intervalo [0,1] para adequação à distribuição Beta
        
        3. **Prior Bayesiano**: Utilizamos uma distribuição Beta(2,2) como prior não-informativo
        
        4. **Posterior**: Calculamos a distribuição posterior combinando o prior com os dados observados
        
        5. **Simulação Monte Carlo**: Geramos 10.000 amostras da distribuição posterior para cada variante
        
        6. **Probabilidade**: Calculamos a probabilidade da variante Nova ser melhor que o Controle como a proporção de amostras onde Nova > Controle
        
        7. **Reescalamento**: Convertemos os resultados de volta para a escala original de RPV
        
        Esta abordagem bayesiana permite quantificar diretamente a probabilidade de uma variante ser superior à outra, incorporando incerteza de forma natural.
        """)
    
    # Conteúdo da análise
    with st.container():
        run_bayes_scipy(st.session_state.data)
        
        st.markdown("""
        🔍 **O que foi feito?** A análise bayesiana utiliza distribuições beta para modelar a incerteza sobre a RPV,
        calculando a probabilidade da nova variante ser melhor que o controle.

        ✅ Fornece uma estimativa da probabilidade de superioridade e recomendação baseada em evidência bayesiana.
        """)

# Página Bayes Beta
elif st.session_state.page == 'bayes_beta':
    st.markdown('<div class="sub-header">📊 Resultado Bayesiano</div>', unsafe_allow_html=True)
    
    # Expander logo após o título
    with st.expander("ℹ️ Como o cálculo foi feito", expanded=False):
        st.markdown("""
        ### Metodologia Bayesiana com Distribuição Normal
        
        1. **Cálculo do RPV**: Para cada dia e variante, calculamos a Receita Por Visita (RPV = receita / sessões)
        
        2. **Modelagem Bayesiana**: Assumimos que o RPV médio de cada variante segue uma distribuição Normal
        
        3. **Prior**: Utilizamos priors baseados nos dados observados, com média igual à média amostral e desvio padrão proporcional ao erro padrão
        
        4. **Simulação Monte Carlo**: Geramos 10.000 amostras da distribuição posterior para cada variante
        
        5. **Probabilidade**: Calculamos a probabilidade da variante Nova ser melhor que o Controle como a proporção de amostras onde Nova > Controle
        
        6. **Intervalo de Credibilidade**: Calculamos o intervalo de 90% de credibilidade para o RPV de cada variante
        
        Esta abordagem bayesiana é mais direta que a versão com Beta e não requer normalização dos dados, sendo adequada quando os valores de RPV seguem aproximadamente uma distribuição normal.
        """)
    
    # Conteúdo da análise
    with st.container():
        run_bayes_beta(st.session_state.data)
        
        st.markdown("""
        🔍 **O que foi feito?** A análise bayesiana com distribuição normal modela diretamente a receita por visita,
        calculando a probabilidade da nova variante ser melhor que o controle.

        ✅ Fornece uma estimativa da probabilidade de superioridade e recomendação baseada em evidência bayesiana.
        """)

# Página Métricas Básicas
elif st.session_state.page == 'metrics_analysis':
    st.markdown('<div class="sub-header">📊 Métricas Básicas</div>', unsafe_allow_html=True)
    
    # Expander logo após o título
    with st.expander("ℹ️ Como o cálculo foi feito", expanded=False):
        st.markdown("""
        ### Metodologia de Análise de Métricas Básicas
        
        1. **Agregação de Dados**: Agrupamos os dados por variante para calcular métricas globais
        
        2. **Métricas Calculadas**:
           - **RPV (Receita Por Visita)**: Média da receita dividida pelo número de sessões
           - **Sessões**: Total de sessões por variante
           - **Receita Total**: Soma da receita por variante
           - **Dias de Teste**: Número de dias únicos no conjunto de dados
        
        3. **Evolução Temporal**: Calculamos as métricas por dia para visualizar tendências ao longo do tempo
        
        4. **Comparação Simples**: Calculamos o lift percentual como (Métrica_nova / Métrica_controle - 1) * 100
        
        5. **Sample Ratio Mismatch (SRM)**:
           - Verificamos se a distribuição de tráfego entre as variantes está conforme o esperado (geralmente 50/50)
           - Calculamos a proporção observada de sessões para cada variante
           - Realizamos um teste binomial para verificar se a diferença entre a proporção observada e a esperada é estatisticamente significativa
           - Um p-valor < 0.05 indica que a distribuição não é aleatória, sugerindo um problema na alocação de tráfego que pode comprometer os resultados do teste
        
        Esta análise fornece uma visão geral descritiva do desempenho das variantes, sem inferência estatística avançada, sendo útil para uma primeira avaliação dos resultados do teste.
        """)
    
    # Conteúdo da análise
    with st.container():
        run_metrics_analysis(st.session_state.data)
        
        st.markdown("""
        🔍 **O que foi feito?** Análise das métricas básicas do teste, incluindo receita por sessão,
        taxa de conversão e evolução diária dos indicadores.

        ✅ Fornece uma visão geral do desempenho das variantes sem inferência estatística avançada.
        """)
