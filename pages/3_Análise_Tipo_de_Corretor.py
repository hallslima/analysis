import pandas as pd
import streamlit as st
import plotly.express as px
from utils import load_data, format_currency, format_integer, render_sidebar

st.set_page_config(layout="wide", page_title="Análise por Tipo de Corretor")

render_sidebar()

# --- Carrega os dados ---
# <<< CORREÇÃO AQUI: Adicionado '_' para receber os dataframes que não usamos nesta página
df_vendas, _, df_inativos, _ = load_data()
if df_vendas is None:
    st.stop()

st.title("🏢 Análise por Tipo de Corretor")
st.markdown("Compare a performance entre os diferentes tipos de corretores e explore as características de cada um.")

# --- Cálculos Gerais para a Visão Comparativa ---
# 1. Cria uma base de corretores única para contagem
df_base_corretores = pd.concat([
    df_vendas[['corretor', 'tipo_de_corretor']],
    df_inativos[['corretor', 'tipo_de_corretor']]
]).drop_duplicates(subset='corretor').reset_index(drop=True)

# 2. Agrega métricas de vendas por tipo de corretor
df_vendas_por_tipo = df_vendas.groupby('tipo_de_corretor').agg(
    total_vendas=('valor_proposta', 'sum'),
    ticket_medio=('valor_proposta', 'mean')
).reset_index()

# 3. Conta o número total de corretores em cada tipo
df_corretores_por_tipo = df_base_corretores.groupby('tipo_de_corretor').agg(
    num_corretores=('corretor', 'count')
).reset_index()

# 4. Junta tudo em um dataframe de performance
df_performance = pd.merge(df_vendas_por_tipo, df_corretores_por_tipo, on='tipo_de_corretor')
df_performance['vendas_por_corretor'] = df_performance['total_vendas'] / df_performance['num_corretores']

# --- Visão Comparativa ---
st.header("Visão Comparativa entre Tipos de Corretor")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Ranking por Total de Vendas")
    df_ranking_vendas = df_performance.sort_values('total_vendas', ascending=True).tail(15)
    fig1 = px.bar(df_ranking_vendas, 
                  x='total_vendas', 
                  y='tipo_de_corretor', 
                  orientation='h', 
                  text='total_vendas',
                  labels={'total_vendas': 'Total de Vendas (R$)', 'tipo_de_corretor': 'Tipo de Corretor'})
    fig1.update_traces(texttemplate='%{text:,.2s}', textposition='outside', marker_color='#f63366')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Ranking por Produtividade (Vendas/Corretor)")
    df_ranking_produtividade = df_performance.sort_values('vendas_por_corretor', ascending=True).tail(15)
    fig2 = px.bar(df_ranking_produtividade, 
                  x='vendas_por_corretor', 
                  y='tipo_de_corretor', 
                  orientation='h', 
                  text='vendas_por_corretor',
                  labels={'vendas_por_corretor': 'Média de Vendas por Corretor (R$)', 'tipo_de_corretor': 'Tipo de Corretor'})
    fig2.update_traces(texttemplate='%{text:,.2s}', textposition='outside', marker_color='#FF8C00')
    st.plotly_chart(fig2, use_container_width=True)


# --- Mergulho Profundo ---
st.markdown("---")
st.header("Análise Detalhada de um Tipo Específico")

# Filtro de seleção
tipos_disponiveis = sorted(df_performance['tipo_de_corretor'].unique())
tipo_selecionado = st.selectbox("Selecione um Tipo de Corretor para analisar", tipos_disponiveis)

# Filtra os dataframes para o tipo selecionado
df_vendas_filtrado = df_vendas[df_vendas['tipo_de_corretor'] == tipo_selecionado]
df_performance_filtrado = df_performance[df_performance['tipo_de_corretor'] == tipo_selecionado].iloc[0]

# KPIs do grupo selecionado
st.subheader(f"Indicadores para: {tipo_selecionado}")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(
    "Total de Vendas", 
    format_currency(df_performance_filtrado['total_vendas']),
    help="Soma do 'valor_proposta' para todos os corretores deste tipo em todo o período dos dados."
)
kpi2.metric(
    "Nº de Corretores", 
    format_integer(df_performance_filtrado['num_corretores']),
    help="Número total de corretores únicos (ativos ou inativos) associados a este tipo na base de dados."
)
kpi3.metric(
    "Vendas por Corretor (Média)", 
    format_currency(df_performance_filtrado['vendas_por_corretor']),
    help="Produtividade média para este tipo de corretor (Total de Vendas / Nº de Corretores)."
)
kpi4.metric(
    "Ticket Médio", 
    format_currency(df_performance_filtrado['ticket_medio']),
    help="Valor médio por proposta de venda para os corretores deste tipo."
)

st.markdown("---")

# Análise de produtos para o grupo
chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Operadoras Mais Vendidas")
    df_operadora = df_vendas_filtrado['operadora'].value_counts().nlargest(10).reset_index().sort_values(by='count')
    fig_op = px.bar(df_operadora, x='count', y='operadora', orientation='h', text='count', labels={'count': 'Nº de Vendas'})
    fig_op.update_traces(textposition='outside')
    st.plotly_chart(fig_op, use_container_width=True)

with chart2:
    st.subheader("Planos Mais Vendidos")
    df_plano = df_vendas_filtrado['plano'].value_counts().nlargest(10).reset_index().sort_values(by='count')
    fig_pl = px.bar(df_plano, x='count', y='plano', orientation='h', text='count', labels={'count': 'Nº de Vendas'})
    fig_pl.update_traces(textposition='outside')
    st.plotly_chart(fig_pl, use_container_width=True)

# Ranking de corretores dentro do grupo
with st.expander(f"Ver ranking de corretores do tipo '{tipo_selecionado}'"):
    df_ranking_corretores = df_vendas_filtrado.groupby('corretor')['valor_proposta'].sum().sort_values(ascending=False).reset_index()
    st.dataframe(df_ranking_corretores.style.format({'valor_proposta': format_currency}))