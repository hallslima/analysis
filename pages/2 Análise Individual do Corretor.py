import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_data, segmenta_corretores, format_currency

st.set_page_config(layout="wide", page_title="Análise de Corretor")

# --- Carrega os dados ---
df_vendas, df_pagamentos = load_data()
df_segmentado_geral, _ = segmenta_corretores(df_vendas)

st.title("Análise Individual de Performance")

# --- Seletor de Corretor ---
lista_corretores = sorted(df_vendas['corretor'].unique())
corretor_selecionado = st.selectbox("Selecione um Corretor", lista_corretores)

# --- Filtrando Dados para o Corretor Selecionado ---
df_vendas_corretor = df_vendas[df_vendas['corretor'] == corretor_selecionado]
df_pagamentos_corretor = df_pagamentos[df_pagamentos['corretor'] == corretor_selecionado]

# --- Barra Lateral com Filtro de Data ---
st.sidebar.header("Filtros da Página")
data_min = df_vendas_corretor['data_vigencia'].min()
data_max = df_vendas_corretor['data_vigencia'].max()
data_inicio = st.sidebar.date_input("Data Início", data_min, min_value=data_min, max_value=data_max, key="data_inicio_individual")
data_fim = st.sidebar.date_input("Data Fim", data_max, min_value=data_min, max_value=data_max, key="data_fim_individual")

# Aplicando o filtro de data
df_vendas_filtrado = df_vendas_corretor[(df_vendas_corretor['data_vigencia'].dt.date >= data_inicio) & (df_vendas_corretor['data_vigencia'].dt.date <= data_fim)]
df_pagamentos_filtrado = df_pagamentos_corretor[(df_pagamentos_corretor['data_baixa'].dt.date >= data_inicio) & (df_pagamentos_corretor['data_baixa'].dt.date <= data_fim)]

st.markdown(f"Analisando dados de **{data_inicio.strftime('%d/%m/%Y')}** a **{data_fim.strftime('%d/%m/%Y')}**")

if df_vendas_filtrado.empty:
    st.warning("O corretor selecionado não possui dados de vendas no período escolhido.")
else:
    # --- Seção de Perfil, Tipo e Supervisor ---
    perfil_ml = "N/A (dados insuficientes)"
    if df_segmentado_geral is not None and corretor_selecionado in df_segmentado_geral['corretor'].values:
        perfil_ml = df_segmentado_geral[df_segmentado_geral['corretor'] == corretor_selecionado]['perfil_corretor'].iloc[0]
    tipos_corretor = df_vendas_filtrado['tipo_de_corretor'].unique()
    tipos_corretor_str = ", ".join(tipos_corretor)
    col_perfil, col_tipo, col_supervisor = st.columns([1, 1, 2])
    with col_perfil:
        st.subheader("Perfil Geral (ML)")
        st.info(f"**{perfil_ml}**")
        st.caption("Baseado no desempenho total.")
    with col_tipo:
        st.subheader("Tipo(s) de Corretor")
        st.info(f"**{tipos_corretor_str}**")
        st.caption("No período selecionado.")
    with col_supervisor:
        st.subheader("Vendas por Supervisor no Período")
        df_supervisor = df_vendas_filtrado.groupby('supervisor')['valor_proposta'].sum().sort_values().reset_index()
        fig_supervisor = px.bar(df_supervisor, x='valor_proposta', y='supervisor', orientation='h', text='valor_proposta')
        fig_supervisor.update_traces(texttemplate='%{text:,.2s}', textposition='outside')
        fig_supervisor.update_layout(yaxis_title=None, xaxis_title=None, showlegend=False)
        st.plotly_chart(fig_supervisor, use_container_width=True)
    st.markdown("---")

    # KPIs
    total_vendas = df_vendas_filtrado['valor_proposta'].sum()
    num_vendas = len(df_vendas_filtrado)
    ticket_medio = total_vendas / num_vendas if num_vendas > 0 else 0
    total_comissao = df_pagamentos_filtrado['amount_to_pay'].sum()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Vendido", format_currency(total_vendas))
    col2.metric("Total de Vendas", f"{num_vendas}")
    col3.metric("Ticket Médio", format_currency(ticket_medio))
    col4.metric("Comissão Paga", format_currency(total_comissao))
    st.markdown("---")

    # --- Gráfico de Série Temporal Interativo ---
    st.subheader("Evolução Temporal de Vendas e Comissões")
    granularidade = st.radio("Ver por:", ("Mês", "Semana", "Dia"), horizontal=True, key='granularidade_temporal')
    if granularidade == 'Mês': regra = 'M'
    elif granularidade == 'Semana': regra = 'W'
    else: regra = 'D'
    vendas_resampled = df_vendas_filtrado.set_index('data_vigencia').resample(regra)['valor_proposta'].sum()
    comissoes_resampled = df_pagamentos_filtrado.set_index('data_baixa').resample(regra)['amount_to_pay'].sum()
    df_temporal = pd.DataFrame({'Vendas': vendas_resampled, 'Comissões': comissoes_resampled}).fillna(0)
    fig_temporal = make_subplots(specs=[[{"secondary_y": True}]])
    fig_temporal.add_trace(go.Scatter(x=df_temporal.index, y=df_temporal['Vendas'], name="Vendas", mode='lines+markers', line=dict(color='#007ACC')), secondary_y=False)
    fig_temporal.add_trace(go.Scatter(x=df_temporal.index, y=df_temporal['Comissões'], name="Comissões", mode='lines+markers', line=dict(color='#FF8C00', dash='dot')), secondary_y=True)
    fig_temporal.update_yaxes(title_text="<b>Total de Vendas (R$)</b>", secondary_y=False)
    fig_temporal.update_yaxes(title_text="<b>Total de Comissões (R$)</b>", secondary_y=True)
    st.plotly_chart(fig_temporal, use_container_width=True)
    st.markdown("---")
    
    # --- Gráficos de Distribuição ---
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.subheader("Vendas por Operadora")
        df_operadora = df_vendas_filtrado['operadora'].value_counts().reset_index().sort_values(by='count', ascending=True)
        fig_operadora = px.bar(df_operadora, x='count', y='operadora', orientation='h', text='count')
        fig_operadora.update_traces(textposition='outside', marker_color='#007ACC')
        fig_operadora.update_layout(yaxis_title=None, xaxis_title="Número de Vendas")
        st.plotly_chart(fig_operadora, use_container_width=True)
    with col_graf2:
        st.subheader("Top 10 Planos Vendidos")
        df_plano = df_vendas_filtrado['plano'].value_counts().nlargest(10).reset_index().sort_values(by='count', ascending=True)
        fig_plano = px.bar(df_plano, x='count', y='plano', orientation='h', text='count')
        fig_plano.update_traces(textposition='outside', marker_color='skyblue')
        fig_plano.update_layout(yaxis_title=None, xaxis_title="Número de Vendas")
        st.plotly_chart(fig_plano, use_container_width=True)

    # --- Tabela de Vendas Recentes ---
    st.subheader("Vendas Recentes no Período")
    st.dataframe(df_vendas_filtrado[['data_vigencia', 'operadora', 'plano', 'valor_proposta']].sort_values('data_vigencia', ascending=False).head(10).style.format({"valor_proposta": format_currency}))
