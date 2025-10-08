import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

@st.cache_data
def load_data():
    """Carrega e limpa os dados dos arquivos CSV da pasta 'data/'."""
    try:
        df_vendas = pd.read_csv('data/vendas.csv', parse_dates=['data_vigencia'])
        df_pagamentos = pd.read_csv('data/comissao.csv', parse_dates=['data_baixa'])
        df_inativos = pd.read_csv('data/corretores_inativos.csv', parse_dates=['data'])
        
        # --- CARREGANDO E TRATANDO O NOVO ARQUIVO FINANCEIRO ---
        # Lendo o arquivo com separador ; e pulando as primeiras linhas vazias
        df_contas_pagar = pd.read_csv('data/contas_a_pagar_set24_set25.csv', delimiter=';', skiprows=1)
        
        # Limpando nomes das colunas
        df_contas_pagar.columns = df_contas_pagar.columns.str.strip()

        # Convertendo colunas de data (formato dd/mm/aaaa)
        date_cols = ['Data de competência', 'Data de vencimento', 'Data prevista', 'Data do último pagamento']
        for col in date_cols:
            df_contas_pagar[col] = pd.to_datetime(df_contas_pagar[col], format='%d/%m/%Y', errors='coerce')

        # Convertendo colunas de valores (formato 1.234,56)
        value_cols = ['Valor original da parcela (R$)', 'Valor pago da parcela (R$)', 
                      'Juros realizado (R$)', 'Valor total pago da parcela (R$)', 'Valor na Categoria 1']
        for col in value_cols:
            df_contas_pagar[col] = df_contas_pagar[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_contas_pagar[col] = pd.to_numeric(df_contas_pagar[col], errors='coerce').fillna(0)

    except FileNotFoundError as e:
        st.error(f"Erro ao carregar dados: O arquivo '{e.filename}' não foi encontrado.")
        return None, None, None, None
    
    # Limpando os outros dataframes
    for df in [df_pagamentos, df_vendas, df_inativos]:
        if df is not None:
            df.columns = df.columns.str.strip()
            for col in df.select_dtypes(['object']).columns:
                df[col] = df[col].str.strip()
            
    return df_vendas, df_pagamentos, df_inativos, df_contas_pagar

@st.cache_data
def segmenta_corretores(df):
    """Executa a clusterização de corretores usando K-Means."""
    if df is None or df.empty or len(df['corretor'].unique()) < 4:
        return None, None
    dados_corretores = df.groupby('corretor').agg(
        total_vendas=('valor_proposta', 'sum'),
        num_vendas=('valor_proposta', 'count'),
        ticket_medio=('valor_proposta', 'mean')
    ).reset_index()
    dados_corretores = dados_corretores[dados_corretores['num_vendas'] > 3]
    num_corretores_validos = len(dados_corretores)
    if num_corretores_validos < 4:
        return None, None
    n_clusters = min(4, num_corretores_validos)
    features = dados_corretores[['total_vendas', 'num_vendas', 'ticket_medio']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    dados_corretores['cluster'] = kmeans.fit_predict(features_scaled)
    cluster_analysis = dados_corretores.groupby('cluster')[['total_vendas', 'num_vendas', 'ticket_medio']].mean().sort_values(by='total_vendas', ascending=False)
    personas = {}
    perfil_nomes = ["🏆 Superestrelas", "🚀 Grande Potencial", "📈 Vendedores de Volume", "🛠️ Em Desenvolvimento"]
    for i, row in enumerate(cluster_analysis.iterrows()):
        personas[row[0]] = perfil_nomes[i]
    dados_corretores['perfil_corretor'] = dados_corretores['cluster'].map(personas)
    cluster_analysis['perfil'] = cluster_analysis.index.map(personas)
    return dados_corretores, cluster_analysis

def format_currency(value):
    """Formata um número para o padrão de moeda brasileiro (R$ 1.234,56)."""
    if pd.isna(value):
        return "R$ 0,00"
    formatted_value = f"{value:,.2f}"
    formatted_value = formatted_value.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    return f"R$ {formatted_value}"

def format_integer(value):
    """Formata um número inteiro para o padrão brasileiro (1.234)."""
    if pd.isna(value):
        return "0"
    return f"{int(value):,}".replace(",", ".")

def render_sidebar():
    """Renderiza os elementos fixos da barra lateral, como o logo."""
    st.sidebar.image("imagens/logo_usina_white.png", width=250)