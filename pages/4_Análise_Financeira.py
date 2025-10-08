import pandas as pd
import streamlit as st
import plotly.express as px
import datetime
from utils import load_data, format_currency, format_integer, render_sidebar

st.set_page_config(layout="wide", page_title="Análise Financeira")

render_sidebar()

# --- Carrega os dados ---
_, _, _, df_contas_pagar = load_data()
if df_contas_pagar is None:
    st.stop()

st.title("Análise Financeira (Contas a Pagar)")

# --- Filtros da Página ---
with st.expander("FILTROS", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        categorias = ["Todas"] + sorted(df_contas_pagar['Categoria 1'].dropna().unique())
        cat_selecionada = st.selectbox("Categoria", categorias)
    with col2:
        centros_custo = ["Todos"] + sorted(df_contas_pagar['Centro de Custo 1'].dropna().unique())
        cc_selecionado = st.selectbox("Centro de Custo", centros_custo)
    with col3:
        data_min = df_contas_pagar['Data de vencimento'].min()
        data_max = df_contas_pagar['Data de vencimento'].max()
        data_inicio = st.date_input("Vencimento Início", data_min, min_value=data_min, max_value=data_max)
    with col4:
        data_fim = st.date_input("Vencimento Fim", data_max, min_value=data_min, max_value=data_max)

# --- Filtragem dos Dados ---
df_filtrado = df_contas_pagar.copy()
if cat_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Categoria 1'] == cat_selecionada]
if cc_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Centro de Custo 1'] == cc_selecionado]
if data_inicio and data_fim:
    df_filtrado = df_filtrado[(df_filtrado['Data de vencimento'].dt.date >= data_inicio) & (df_filtrado['Data de vencimento'].dt.date <= data_fim)]

# --- Layout com Abas ---
st.markdown(f"Exibindo dados de **{data_inicio.strftime('%d/%m/%Y')}** a **{data_fim.strftime('%d/%m/%Y')}**")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral Financeira", "Fluxo de Caixa Futuro", "Análise de Fornecedores", "Dados Detalhados"])

with tab1:
    st.header("Indicadores do Período")
    
    # KPIs
    total_pago = df_filtrado['Valor total pago da parcela (R$)'].sum()
    total_juros = df_filtrado['Juros realizado (R$)'].sum()
    proximos_30_dias = df_contas_pagar[
        (df_contas_pagar['Data de vencimento'] >= pd.to_datetime('today')) &
        (df_contas_pagar['Data de vencimento'] <= pd.to_datetime('today') + datetime.timedelta(days=30))
    ]['Valor original da parcela (R$)'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Total Pago no Período", 
        format_currency(total_pago),
        help="Soma do 'Valor total pago da parcela' para todas as contas que vencem no período selecionado."
    )
    col2.metric(
        "Total de Juros Pagos",
        format_currency(total_juros),
        help="Soma dos juros pagos para as contas no período selecionado."
    )
    col3.metric(
        "A Vencer (Próx. 30 dias)",
        format_currency(proximos_30_dias),
        help="Soma do 'Valor original da parcela' de todas as contas com vencimento nos próximos 30 dias a partir de hoje."
    )
    st.markdown("---")
    
    # Gráficos de Composição
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.subheader("Top 10 Despesas por Categoria")
        df_categoria = df_filtrado.groupby('Categoria 1')['Valor total pago da parcela (R$)'].sum().nlargest(10).sort_values()
        fig_cat = px.bar(df_categoria, x=df_categoria.values, y=df_categoria.index, orientation='h', text=df_categoria.values)
        fig_cat.update_traces(texttemplate='%{text:,.2s}', textposition='outside', marker_color='#f63366')
        fig_cat.update_layout(yaxis_title=None, xaxis_title="Total Pago (R$)")
        st.plotly_chart(fig_cat, use_container_width=True)

    with gcol2:
        st.subheader("Despesas por Centro de Custo")
        df_cc = df_filtrado.groupby('Centro de Custo 1')['Valor total pago da parcela (R$)'].sum().sort_values()
        fig_cc = px.bar(df_cc, x=df_cc.values, y=df_cc.index, orientation='h', text=df_cc.values)
        fig_cc.update_traces(texttemplate='%{text:,.2s}', textposition='outside')
        fig_cc.update_layout(yaxis_title=None, xaxis_title="Total Pago (R$)")
        st.plotly_chart(fig_cc, use_container_width=True)

with tab2:
    st.header("Projeção de Contas a Pagar")
    st.info("Este gráfico mostra o valor original das parcelas com vencimento nos próximos meses, independentemente dos filtros.")

    df_futuro = df_contas_pagar[df_contas_pagar['Data de vencimento'].dt.date >= datetime.date.today()]
    df_fluxo = df_futuro.set_index('Data de vencimento').resample('M')['Valor original da parcela (R$)'].sum().reset_index()
    df_fluxo['Mês'] = df_fluxo['Data de vencimento'].dt.strftime('%Y-%m')

    fig_fluxo = px.bar(df_fluxo, x='Mês', y='Valor original da parcela (R$)', text='Valor original da parcela (R$)')
    fig_fluxo.update_traces(texttemplate='%{text:,.2s}', textposition='outside')
    fig_fluxo.update_layout(yaxis_title="Total a Pagar (R$)", xaxis_title="Mês de Vencimento")
    st.plotly_chart(fig_fluxo, use_container_width=True)

with tab3:
    st.header("Análise de Fornecedores")
    
    st.subheader("Top 20 Fornecedores por Valor Pago")
    df_fornecedores = df_filtrado.groupby('Nome do fornecedor')['Valor total pago da parcela (R$)'].sum().nlargest(20).sort_values()
    fig_fornec = px.bar(df_fornecedores, x=df_fornecedores.values, y=df_fornecedores.index, orientation='h', text=df_fornecedores.values)
    fig_fornec.update_traces(texttemplate='%{text:,.2s}', textposition='outside')
    fig_fornec.update_layout(yaxis_title=None, xaxis_title="Total Pago (R$)")
    st.plotly_chart(fig_fornec, use_container_width=True)

with tab4:
    st.header("Dados Detalhados")
    st.dataframe(df_filtrado)