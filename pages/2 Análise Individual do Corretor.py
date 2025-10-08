import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_data, segmenta_corretores, format_currency, format_integer, render_sidebar

st.set_page_config(layout="wide", page_title="Análise de Corretor")

render_sidebar()

# --- Carrega todos os dados ---
# <<< CORREÇÃO AQUI: Adicionado '_' para receber o quarto dataframe
df_vendas, df_pagamentos, df_inativos, _ = load_data()
if df_vendas is None:
    st.stop()

df_segmentado_geral, _ = segmenta_corretores(df_vendas)

st.title("🔎 Análise Individual de Performance")
st.markdown("Selecione um corretor para uma análise detalhada de desempenho e atividade.")

# --- Seletor de Corretor no topo da página ---
corretor_selecionado = st.selectbox("Selecione um Corretor", sorted(df_vendas['corretor'].unique()), label_visibility="collapsed")

# --- Filtrando Dados para o Corretor Selecionado ---
df_vendas_corretor = df_vendas[df_vendas['corretor'] == corretor_selecionado]
df_pagamentos_corretor = df_pagamentos[df_pagamentos['corretor'] == corretor_selecionado]
df_inativos_corretor = df_inativos[df_inativos['corretor'] == corretor_selecionado]

if df_vendas_corretor.empty and df_inativos_corretor.empty:
    st.warning("Este corretor não possui dados de vendas ou inatividade.")
else:
    # --- Cálculos de Médias para Comparação ---
    media_ticket_geral = df_vendas['valor_proposta'].mean()
    df_vendas_total = df_vendas.groupby('corretor')['valor_proposta'].sum()
    df_pagamentos_total = df_pagamentos.groupby('corretor')['amount_to_pay'].sum()
    df_merged = pd.merge(df_vendas_total, df_pagamentos_total, on='corretor', how='inner')
    media_comissao_geral = (df_merged['amount_to_pay'].sum() / df_merged['valor_proposta'].sum()) * 100 if df_merged['valor_proposta'].sum() > 0 else 0


    # --- Layout com Abas ---
    tab1, tab2, tab3 = st.tabs(["Visão Geral do Corretor", "Análise por Produto", "Vendas Recentes"])

    with tab1:
        # --- Seção de Perfil ---
        perfil_ml = "N/A"
        if df_segmentado_geral is not None and corretor_selecionado in df_segmentado_geral['corretor'].values:
            perfil_ml = df_segmentado_geral[df_segmentado_geral['corretor'] == corretor_selecionado]['perfil_corretor'].iloc[0]
        
        tipos_corretor = ", ".join(df_vendas_corretor['tipo_de_corretor'].unique()) if not df_vendas_corretor.empty else "N/A"
        
        st.subheader("Perfil do Corretor")
        col_perfil1, col_perfil2 = st.columns(2)
        with col_perfil1:
            st.markdown(f"**Perfil (ML):** `{perfil_ml}`")
        with col_perfil2:
            st.markdown(f"**Tipo(s):** `{tipos_corretor}`")
        st.markdown("---")

        # --- KPIs com Comparação ---
        st.subheader("Indicadores Chave de Performance (KPIs)")
        total_vendas = df_vendas_corretor['valor_proposta'].sum()
        num_vendas = len(df_vendas_corretor)
        ticket_medio = total_vendas / num_vendas if num_vendas > 0 else 0
        total_comissao = df_pagamentos_corretor['amount_to_pay'].sum()
        taxa_comissao = (total_comissao / total_vendas) * 100 if total_vendas > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Vendido", format_currency(total_vendas))
        col2.metric("Nº de Vendas", format_integer(num_vendas))
        col3.metric("Ticket Médio", format_currency(ticket_medio), delta=f"{format_currency(ticket_medio - media_ticket_geral)} vs. Média")
        col4.metric("Taxa de Comissão", f"{taxa_comissao:.2f}%", delta=f"{(taxa_comissao - media_comissao_geral):.2f} p.p. vs. Média")
        st.markdown("---")
        
        # --- Gráfico Comparativo: Vendas vs. Comissão ---
        st.subheader("Comparativo Mensal: Vendas vs. Comissões")
        
        vendas_mensais = df_vendas_corretor.set_index('data_vigencia').resample('M')['valor_proposta'].sum()
        comissoes_mensais = df_pagamentos_corretor.set_index('data_baixa').resample('M')['amount_to_pay'].sum()
        
        df_monthly = pd.DataFrame({'Vendas': vendas_mensais, 'Comissões': comissoes_mensais}).fillna(0).reset_index()
        df_monthly['Mês'] = df_monthly['index'].dt.strftime('%Y-%m')
        
        df_melted = pd.melt(df_monthly, id_vars=['Mês'], value_vars=['Vendas', 'Comissões'], var_name='Métrica', value_name='Valor')

        fig_vendas_comissao = px.bar(
            df_melted,
            x='Mês',
            y='Valor',
            color='Métrica',
            barmode='group',
            text='Valor',
            color_discrete_map={'Vendas': '#007ACC', 'Comissões': '#FF8C00'},
            labels={'Valor': 'Valor (R$)'}
        )
        fig_vendas_comissao.update_traces(texttemplate='%{text:,.2s}', textposition='outside')
        st.plotly_chart(fig_vendas_comissao, use_container_width=True)
        st.markdown("---")
        
        # --- Gráfico de Status Mensal ---
        st.subheader("Status Mensal de Atividade")
        
        start_date = min(df_vendas['data_vigencia'].min(), df_inativos['data'].min())
        end_date = max(df_vendas['data_vigencia'].max(), df_inativos['data'].max())
        all_months_index = pd.date_range(start=start_date, end=end_date, freq='MS')
        df_status = pd.DataFrame(index=all_months_index)

        if not df_vendas_corretor.empty:
            meses_ativos = df_vendas_corretor.set_index('data_vigencia').resample('MS').size()
            meses_ativos = meses_ativos[meses_ativos > 0]
            df_status['ativo'] = meses_ativos.reindex(df_status.index).fillna(0).astype(int)
        else:
            df_status['ativo'] = 0

        if not df_inativos_corretor.empty:
            meses_inativos = df_inativos_corretor.set_index('data').resample('MS').size()
            meses_inativos = meses_inativos[meses_inativos > 0]
            df_status['inativo'] = meses_inativos.reindex(df_status.index).fillna(0).astype(int)
        else:
            df_status['inativo'] = 0

        df_status['status'] = 0 
        df_status.loc[df_status['inativo'] > 0, 'status'] = -1
        df_status.loc[df_status['ativo'] > 0, 'status'] = 1
        
        df_status['status_label'] = df_status['status'].map({1: 'Ativo', -1: 'Inativo', 0: 'Sem Registro'})

        fig_status = go.Figure()
        fig_status.add_trace(go.Scatter(
            x=df_status.index, y=df_status['status'],
            mode='lines+markers',
            marker=dict(color=df_status['status'].map({1: 'green', -1: 'red', 0: 'grey'}), size=10),
            line=dict(color='lightgrey'),
            text=df_status['status_label'],
            hovertemplate='<b>Mês</b>: %{x|%B de %Y}<br><b>Status</b>: %{text}<extra></extra>'
        ))
        fig_status.update_layout(
            yaxis=dict(tickvals=[-1, 0, 1], ticktext=['Inativo', 'Sem Registro', 'Ativo']),
            xaxis_title="Linha do Tempo", yaxis_title="Status"
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with tab2:
        st.header("Análise de Vendas por Produto")
        if df_vendas_corretor.empty:
            st.warning("Sem dados de vendas para exibir.")
        else:
            col_graf1, col_graf2 = st.columns(2)
            with col_graf1:
                st.subheader("Vendas por Operadora")
                df_operadora = df_vendas_corretor['operadora'].value_counts().reset_index().sort_values(by='count', ascending=True)
                fig_operadora = px.bar(df_operadora, x='count', y='operadora', orientation='h', text='count')
                fig_operadora.update_traces(texttemplate='%{text:,.0f}'.replace(",", "."), textposition='outside', marker_color='#007ACC')
                fig_operadora.update_layout(yaxis_title=None, xaxis_title="Número de Vendas")
                st.plotly_chart(fig_operadora, use_container_width=True)
            with col_graf2:
                st.subheader("Top 10 Planos Vendidos")
                df_plano = df_vendas_corretor['plano'].value_counts().nlargest(10).reset_index().sort_values(by='count', ascending=True)
                fig_plano = px.bar(df_plano, x='count', y='plano', orientation='h', text='count')
                fig_plano.update_traces(texttemplate='%{text:,.0f}'.replace(",", "."), textposition='outside', marker_color='skyblue')
                fig_plano.update_layout(yaxis_title=None, xaxis_title="Número de Vendas")
                st.plotly_chart(fig_plano, use_container_width=True)
            
    with tab3:
        st.header("Tabela de Vendas Recentes")
        if df_vendas_corretor.empty:
            st.warning("Sem dados de vendas para exibir.")
        else:
            st.dataframe(df_vendas_corretor[['data_vigencia', 'operadora', 'plano', 'valor_proposta']].sort_values('data_vigencia', ascending=False).head(20).style.format({"valor_proposta": format_currency}))