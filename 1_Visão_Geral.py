import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import plotly.express as px
from utils import load_data, segmenta_corretores, format_currency, format_integer, render_sidebar

st.set_page_config(layout="wide", page_title="Dashboard de Vendas | Visão Geral")

render_sidebar()

# --- Funções de Gráfico ---
def criar_grafico_top_corretores(df):
    if df.empty:
        st.warning("Não há dados de vendas para a seleção atual.")
        return None
    top_10 = df.groupby('corretor')['valor_proposta'].sum().nlargest(10).sort_values()
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['lightgray'] * (len(top_10) - 1) + ['#007ACC']
    bars = ax.barh(top_10.index, top_10.values, color=colors)
    ax.set_title("Top 10 Corretores por Vendas", loc='left', fontsize=16)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'R$ {int(x/1000)}k'))
    ax.spines[['top', 'right', 'left']].set_visible(False)
    plt.tight_layout()
    return fig

def criar_treemap_planos(df):
    if df.empty: return None
    vendas_plano = df.groupby('plano')['valor_proposta'].sum().reset_index()
    vendas_plano['valor_formatado'] = vendas_plano['valor_proposta'].apply(format_currency)
    fig = px.treemap(vendas_plano, 
                     path=['plano'], 
                     values='valor_proposta',
                     custom_data=['valor_formatado'],
                     title='Distribuição de Vendas por Plano',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textinfo='label+percent entry', 
                      hovertemplate='<b>%{label}</b><br>Vendas: %{customdata[0]}<extra></extra>')
    return fig

def criar_treemap_operadoras(df):
    if df.empty: return None
    vendas_operadora = df.groupby('operadora')['valor_proposta'].sum().reset_index()
    vendas_operadora['valor_formatado'] = vendas_operadora['valor_proposta'].apply(format_currency)
    fig = px.treemap(vendas_operadora, 
                     path=['operadora'], 
                     values='valor_proposta',
                     custom_data=['valor_formatado'],
                     title='Distribuição de Vendas por Operadora',
                     color_discrete_sequence=px.colors.qualitative.Pastel2)
    fig.update_traces(textinfo='label+percent entry', 
                      hovertemplate='<b>%{label}</b><br>Vendas: %{customdata[0]}<extra></extra>')
    return fig

def criar_grafico_vendas_tempo(df):
    if df.empty: return None
    vendas_mensais = df.set_index('data_vigencia').resample('M')['valor_proposta'].sum().reset_index()
    fig = px.line(vendas_mensais, x='data_vigencia', y='valor_proposta', markers=True,
                  labels={'data_vigencia': 'Mês', 'valor_proposta': 'Total de Vendas'})
    fig.update_traces(hovertemplate='<b>Mês</b>: %{x|%B de %Y}<br><b>Vendas</b>: %{y:,.2f}<extra></extra>')
    fig.update_layout(title_text="Evolução das Vendas no Período", title_x=0.5)
    return fig

# --- Carregamento dos Dados ---
df_vendas, df_pagamentos = load_data()
if df_vendas is None:
    st.stop()

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar.expander("FILTROS", expanded=True):
    st.header("Filtros Globais")
    lista_supervisores = list(df_vendas['supervisor'].unique())
    lista_supervisores.insert(0, "Todos")
    supervisor_selecionado = st.selectbox("Supervisor", lista_supervisores)
    lista_tipos = list(df_vendas['tipo_de_corretor'].unique())
    lista_tipos.insert(0, "Todos")
    tipo_selecionado = st.selectbox("Tipo de Corretor", lista_tipos)
    data_min, data_max = df_vendas['data_vigencia'].min(), df_vendas['data_vigencia'].max()
    data_inicio = st.date_input("Data Início", data_min, min_value=data_min, max_value=data_max)
    data_fim = st.date_input("Data Fim", data_max, min_value=data_min, max_value=data_max)

# --- Filtragem dos Dados ---
df_filtrado = df_vendas.copy()
if supervisor_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['supervisor'] == supervisor_selecionado]
if tipo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['tipo_de_corretor'] == tipo_selecionado]
if data_inicio and data_fim:
    df_filtrado = df_filtrado[(df_filtrado['data_vigencia'].dt.date >= data_inicio) & (df_filtrado['data_vigencia'].dt.date <= data_fim)]

# --- Layout Principal com Abas ---
st.title("🚀 Dashboard de Performance de Vendas")
st.markdown(f"Dados de **{data_inicio.strftime('%d/%m/%Y')}** a **{data_fim.strftime('%d/%m/%Y')}**")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "📄 Análise de Planos e Operadoras", "🤖 Segmentação de Corretores (ML)", "💾 Dados Detalhados"])

with tab1:
    st.header("Principais Indicadores")
    total_vendas = df_filtrado['valor_proposta'].sum()
    num_vendas = len(df_filtrado)
    ticket_medio = total_vendas / num_vendas if num_vendas > 0 else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", format_currency(total_vendas))
    col2.metric("Número de Vendas", format_integer(num_vendas))
    col3.metric("Ticket Médio", format_currency(ticket_medio))
    st.markdown("---")
    
    fig_vendas_tempo = criar_grafico_vendas_tempo(df_filtrado)
    if fig_vendas_tempo:
        st.plotly_chart(fig_vendas_tempo, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Desempenho dos Corretores")
    fig_top_corretores = criar_grafico_top_corretores(df_filtrado)
    if fig_top_corretores: 
        st.pyplot(fig_top_corretores)

with tab2:
    st.header("Análise de Vendas por Plano e Operadora")
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.info("Use o treemap para identificar os planos mais vendidos.")
        fig_treemap_planos = criar_treemap_planos(df_filtrado)
        if fig_treemap_planos:
            st.plotly_chart(fig_treemap_planos, use_container_width=True)
    with col_graf2:
        st.info("Use o treemap para identificar as operadoras com maior volume.")
        fig_treemap_operadoras = criar_treemap_operadoras(df_filtrado)
        if fig_treemap_operadoras: 
            st.plotly_chart(fig_treemap_operadoras, use_container_width=True)

with tab3:
    st.header("Segmentação de Corretores com Machine Learning")
    st.info("O modelo de IA analisou e agrupou os corretores em perfis de desempenho com base nos filtros aplicados.")
    df_segmentado, df_analise_cluster = segmenta_corretores(df_filtrado)
    if df_segmentado is not None:
        st.subheader("Resumo dos Perfis Encontrados")
        df_analise_cluster_styled = df_analise_cluster.style.format({"total_vendas": format_currency, "ticket_medio": format_currency, "num_vendas": format_integer})
        st.dataframe(df_analise_cluster_styled)
        st.subheader("O que cada perfil significa?")
        for perfil_nome in df_analise_cluster['perfil'].unique():
            with st.expander(f"Saiba mais sobre o perfil: **{perfil_nome}**"):
                if perfil_nome == "🏆 Superestrelas":
                    st.markdown("- **Características:** Este grupo tem o **maior volume total de vendas** e um **ticket médio elevado**.\n- **Estratégia Sugerida:** Reconhecer e recompensar publicamente. Estudar suas técnicas para replicar em treinamentos.")
                elif perfil_nome == "🚀 Grande Potencial":
                    st.markdown("- **Características:** Possuem um **ticket médio muito alto**, mas com um volume de vendas menor que as Superestrelas.\n- **Estratégia Sugerida:** Incentivar o aumento do volume de propostas. Podem atuar como mentores para ensinar a vender planos de maior valor.")
                elif perfil_nome == "📈 Vendedores de Volume":
                    st.markdown("- **Características:** Fecham um **grande número de negócios**, mas com um ticket médio mais baixo.\n- **Estratégia Sugerida:** Oferecer bônus por volume. Realizar treinamentos focados em técnicas de *upsell*.")
                elif perfil_nome == "🛠️ Em Desenvolvimento":
                    st.markdown("- **Características:** Apresentam os menores valores em volume de vendas, número de propostas e ticket médio.\n- **Estratégia Sugerida:** Acompanhamento próximo do supervisor e treinamentos intensivos.")
        st.subheader("Explore os Corretores Segmentados")
        perfis_disponiveis = list(df_segmentado['perfil_corretor'].unique())
        perfis_disponiveis.insert(0, "Todos os Perfis")
        perfil_selecionado = st.selectbox("Filtrar por Perfil", perfis_disponiveis)
        df_segmentado_filtrado = df_segmentado.copy()
        if perfil_selecionado != "Todos os Perfis":
            df_segmentado_filtrado = df_segmentado[df_segmentado['perfil_corretor'] == perfil_selecionado]
        df_segmentado_styled = df_segmentado_filtrado[['corretor', 'perfil_corretor', 'total_vendas', 'num_vendas', 'ticket_medio']].style.format({"total_vendas": format_currency, "ticket_medio": format_currency, "num_vendas": format_integer})
        st.dataframe(df_segmentado_styled)
        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        csv_segmentacao = convert_df_to_csv(df_segmentado_filtrado)
        st.download_button(label="📥 Baixar Lista de Segmentação como CSV", data=csv_segmentacao, file_name=f'segmentacao_{perfil_selecionado.lower().replace(" ", "_")}.csv', mime='text/csv')
    else:
        st.warning("Não há dados suficientes para realizar a segmentação com a seleção de filtros atual.")

with tab4:
    st.header("Explore os Dados Detalhados")
    df_filtrado_styled = df_filtrado.style.format({"valor_proposta": format_currency})
    st.dataframe(df_filtrado_styled)
    csv_geral = convert_df_to_csv(df_filtrado)
    st.download_button(label="📥 Baixar dados gerais como CSV", data=csv_geral, file_name='dados_filtrados.csv', mime='text/csv')