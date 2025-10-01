import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

@st.cache_data
def load_data():
    """Carrega e limpa os dados dos arquivos CSV da pasta 'data/'."""
    # <<< NOMES FINAIS E CORRETOS DOS ARQUIVOS >>>
    df_vendas = pd.read_csv('data/vendas.csv', parse_dates=['data_vigencia'])
    df_pagamentos = pd.read_csv('data/comissao.csv', parse_dates=['data_baixa'])
    
    for df in [df_pagamentos, df_vendas]:
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(['object']).columns:
            df[col] = df[col].str.strip()
            
    return df_vendas, df_pagamentos

@st.cache_data
def segmenta_corretores(df):
    """Executa a clusterização de corretores usando K-Means."""
    if df.empty or len(df['corretor'].unique()) < 4:
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
    """Formata um número para o padrão de moeda brasileiro."""
    return f"R$ {value:,.2f}"
