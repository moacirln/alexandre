import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import dataframe as dt
@st.cache_data(persist="disk")
def importar_dados(API):
    df_deals = dt.criar_deals_id(API)
    df_calendario = pd.read_csv('calendario.csv')
    df_metas = pd.read_csv('metas.csv')
    df_metas['meta_valor_vendas_ganhas'] = df_metas['meta_valor_vendas_ganhas'].astype(str)
    df_metas['meta_posvenda_valor_vendas'] = df_metas['meta_posvenda_valor_vendas'].astype(str)
    df_metas['meta_valor_vendas_ganhas'] = df_metas['meta_valor_vendas_ganhas'].str.replace(',', '')
    df_metas['meta_posvenda_valor_vendas'] = df_metas['meta_posvenda_valor_vendas'].str.replace(',', '')
    df_atividades = dt.criar_atividades(API)
    df_users = dt.criar_usuários(API)
    return df_deals,df_calendario,df_metas,df_atividades,df_users
@st.cache_data(persist="disk")
def importar_dados2(API,df_deals):
    df_dados = dt.criar_dados(API, df_deals)
    return df_dados

def main():
    #Configuração página inicial
    st.set_page_config(page_title='Dashboard', layout= 'wide', initial_sidebar_state='collapsed')
    st.image('LOGO.png')

    API = st.text_input('API:')
    if API:
        df_deals, df_calendario, df_metas, df_atividades, df_users = importar_dados(API)
        df_dados = importar_dados2(API, df_deals)
        botao_dados = st.button('Recarregar Dados')
        if botao_dados:
            importar_dados.clear()


        sidebar = st.sidebar
        sidebar.header("PERSONALIZE SUA ANÁLISE")
        user = sidebar.selectbox("Escolha o colaborador",["Todos"] + list(df_deals['user_id'].unique()))
        filtro_semana = sidebar.selectbox('Análise Semanal',["Todas"] + list(df_calendario['semana'].unique()))

        if filtro_semana == "Todas":
            period_start_datetime = pd.to_datetime(df_calendario['period_start'].iloc[0])
            formatted_date = period_start_datetime.strftime('%d-%m-%Y')
            period_end_datetime = pd.to_datetime(df_calendario['period_end'].iloc[23])
            formatted_dateend = period_end_datetime.strftime('%d-%m-%Y')
            sidebar.subheader('Perído de Análise:')
            sidebar.subheader(f'{formatted_date} e {formatted_dateend} ')
            pass
        else:
            df_calendario = df_calendario[df_calendario['semana'] == filtro_semana]
            period_start_datetime = pd.to_datetime(df_calendario['period_start'].iloc[0])
            formatted_date = period_start_datetime.strftime('%d-%m-%Y')
            period_end_datetime = pd.to_datetime(df_calendario['period_end'].iloc[0])
            formatted_dateend = period_end_datetime.strftime('%d-%m-%Y')
            sidebar.subheader('Perído de Análise:')
            sidebar.subheader(f'{formatted_date} e {formatted_dateend} ')

        if user == "Todos":
            pass
        else:
            df_deals = df_deals[df_deals['user_id'] == user]
            df_atividades = df_atividades[df_atividades['user_id'] == df_deals['user_id'].iloc[0]]
            df_metas = df_metas[df_metas['user_id'] == df_metas['user_id'].iloc[0]]

        df_master = dt.criar_leads(df_calendario, df_dados)
        df_master = dt.criar_qualificacao(df_atividades, df_calendario)
        df_master = dt.criar_leads_qualificados(df_atividades, df_calendario)
        df_master = dt.criar_proposta_venda(df_atividades, df_calendario)
        df_master = dt.criar_negociacao_venda(df_atividades, df_calendario)
        df_master = dt.criar_vendas(df_deals, df_calendario)
        df_master = dt.criar_proposta_negociacoes_posvenda(df_calendario, df_dados)
        df_master = dt.criar_posvendas(df_deals, df_calendario)

        df_metas = df_metas.drop(['user_id'], axis=1)
        df_metas['meta_valor_vendas_ganhas'] = df_metas['meta_valor_vendas_ganhas'].astype(float)
        df_metas['meta_posvenda_valor_vendas'] = df_metas['meta_posvenda_valor_vendas'].astype(float)
        df_metas = df_metas.groupby('semana').sum()
        df_master = pd.merge(df_master, df_metas, on='semana')
        df_master = df_master.drop(['bin','Leads1','Leads2'], axis=1)
        df_master['Lead_GAP'] = df_master['Leads'] - df_master['meta_leads']
        df_master['Lead_(%Meta)'] = df_master['Leads']/df_master['meta_leads']
        df_master['Qualificação_GAP'] = df_master['Qualificação'] - df_master['meta_qualificações']
        df_master['Qualificação_(%Meta)'] = df_master['Qualificação']/df_master['meta_qualificações']
        df_master['Leads Qualificados_GAP'] = df_master['Leads Qualificados'] - df_master['meta_leads_qualificados']
        df_master['Leads Qualificados_(%Meta)'] = df_master['Leads Qualificados'] / df_master['meta_leads_qualificados']
        df_master['Proposta_GAP'] = df_master['Proposta'] - df_master['meta_propostas']
        df_master['Proposta_(%Meta)'] = df_master['Proposta'] / df_master['meta_propostas']
        df_master['Negociação_GAP'] = df_master['Negociação'] - df_master['meta_negociações']
        df_master['Negociação_(%Meta)'] = df_master['Negociação'] / df_master['meta_negociações']
        df_master['Qtd.Venda_GAP'] = df_master['Qtd. Venda'] - df_master['meta_vendas_ganhas']
        df_master['Qtd.Venda_GAP_(%Meta)'] = df_master['Qtd. Venda'] / df_master['meta_vendas_ganhas']
        df_master['Valor Venda_GAP'] = df_master['Valor Venda'] - df_master['meta_valor_vendas_ganhas']
        df_master['Valor Venda_(%Meta)'] = df_master['Valor Venda'] / df_master['meta_valor_vendas_ganhas']
        df_master['Proposta PosVenda_GAP'] = df_master['proposta_posvenda'] - df_master['meta_posvenda_proposta']
        df_master['Proposta PosVenda_(%Meta)'] = df_master['proposta_posvenda'] / df_master['meta_posvenda_proposta']
        df_master['Negociação PosVenda_GAP'] = df_master['negociacao_posvenda'] - df_master['meta_posvenda_negociações']
        df_master['Negociação PosVenda_(%Meta)'] = df_master['negociacao_posvenda'] / df_master['meta_posvenda_negociações']
        df_master['Qtd. PosVenda_GAP'] = df_master['Qtd. PosVenda'] - df_master['meta_posvendas_negócios_ganhos']
        df_master['Qtd. PosVenda_(%Meta)'] = df_master['Qtd. PosVenda'] / df_master['meta_posvendas_negócios_ganhos']
        df_master['Valor PosVenda_GAP'] = df_master['Valor PosVenda'] - df_master['meta_posvenda_valor_vendas']
        df_master['Valor PosVenda_(%Meta)'] = df_master['Valor PosVenda'] / df_master['meta_posvenda_valor_vendas']

        df_master['Proposta (Venda+Pos)'] = df_master['Proposta']+df_master['proposta_posvenda']
        df_master['meta_Proposta (Venda+Pos)'] = df_master['meta_propostas']+df_master['meta_posvenda_proposta']
        df_master['Proposta (Venda+Pos)_GAP'] = df_master['Proposta (Venda+Pos)'] + df_master['meta_Proposta (Venda+Pos)']
        df_master['Proposta (Venda+Pos)_(%Meta)'] = df_master['Proposta (Venda+Pos)'] / df_master['meta_Proposta (Venda+Pos)']

        df_master['Negociação (Venda+Pos)'] = df_master['Negociação']+df_master['negociacao_posvenda']
        df_master['meta_Negociação (Venda+Pos)'] = df_master['meta_negociações']+df_master['meta_posvenda_negociações']
        df_master['Negociação (Venda+Pos)_GAP'] = df_master['Negociação (Venda+Pos)'] + df_master['meta_Negociação (Venda+Pos)']
        df_master['Negociação (Venda+Pos)_(%Meta)'] = df_master['Negociação (Venda+Pos)'] / df_master['meta_Negociação (Venda+Pos)']

        df_master['Qtd. Venda (Venda+Pos)'] = df_master['Qtd. Venda']+df_master['Qtd. PosVenda']
        df_master['meta_Qtd. Venda (Venda+Pos)'] = df_master['meta_vendas_ganhas']+df_master['meta_posvendas_negócios_ganhos']
        df_master['Qtd. Venda (Venda+Pos)_GAP'] = df_master['Qtd. Venda (Venda+Pos)'] + df_master['meta_Qtd. Venda (Venda+Pos)']
        df_master['Qtd. Venda (Venda+Pos)_(%Meta)'] = df_master['Qtd. Venda (Venda+Pos)'] / df_master['meta_Qtd. Venda (Venda+Pos)']

        df_master['Valor Venda (Venda+Pos)'] = df_master['Valor Venda']+df_master['Valor PosVenda']
        df_master['meta_Valor Venda (Venda+Pos)'] = df_master['meta_valor_vendas_ganhas']+df_master['meta_posvenda_valor_vendas']
        df_master['Valor Venda (Venda+Pos)_GAP'] = df_master['Valor Venda (Venda+Pos)'] + df_master['meta_Valor Venda (Venda+Pos)']
        df_master['Valor Venda (Venda+Pos)_(%Meta)'] = df_master['Valor Venda (Venda+Pos)'] / df_master['meta_Valor Venda (Venda+Pos)']

        df_master = df_master[['semana','Leads','meta_leads','Lead_(%Meta)','Lead_GAP','Qualificação','meta_qualificações','Qualificação_GAP',
                               'Qualificação_(%Meta)','Leads Qualificados','meta_leads_qualificados','Leads Qualificados_GAP','Leads Qualificados_(%Meta)','Proposta',
                               'meta_propostas','Proposta_GAP','Proposta_(%Meta)','Negociação','meta_negociações','Negociação_GAP','Negociação_(%Meta)',
                               'Qtd. Venda','meta_vendas_ganhas','Qtd.Venda_GAP','Qtd.Venda_GAP_(%Meta)','Valor Venda',
                               'meta_valor_vendas_ganhas','Valor Venda_GAP','Valor Venda_(%Meta)','proposta_posvenda',
                               'meta_posvenda_proposta','Proposta PosVenda_GAP','Proposta PosVenda_(%Meta)','negociacao_posvenda',
                               'meta_posvenda_negociações','Negociação PosVenda_GAP','Negociação PosVenda_(%Meta)','Qtd. PosVenda',
                               'meta_posvendas_negócios_ganhos','Qtd. PosVenda_GAP','Qtd. PosVenda_(%Meta)','Valor PosVenda','meta_posvenda_valor_vendas','Valor PosVenda_GAP','Valor PosVenda_(%Meta)',
                               'Proposta (Venda+Pos)','meta_Proposta (Venda+Pos)',
                               'Proposta (Venda+Pos)_GAP','Proposta (Venda+Pos)_(%Meta)','Negociação (Venda+Pos)','meta_Negociação (Venda+Pos)','Negociação (Venda+Pos)_GAP',
                               'Negociação (Venda+Pos)_(%Meta)','Qtd. Venda (Venda+Pos)','meta_Qtd. Venda (Venda+Pos)','Qtd. Venda (Venda+Pos)_GAP','Qtd. Venda (Venda+Pos)_(%Meta)',
                               'Valor Venda (Venda+Pos)','meta_Valor Venda (Venda+Pos)','Valor Venda (Venda+Pos)_GAP','Valor Venda (Venda+Pos)_(%Meta)']]

        df_prevenda = df_master[['semana','Leads','meta_leads','Lead_(%Meta)','Lead_GAP','Qualificação','meta_qualificações','Qualificação_GAP',
                               'Qualificação_(%Meta)','Leads Qualificados','meta_leads_qualificados','Leads Qualificados_GAP','Leads Qualificados_(%Meta)']]

        df_venda = df_master[['semana','Proposta',
                               'meta_propostas','Proposta_GAP','Proposta_(%Meta)','Negociação','meta_negociações','Negociação_GAP','Negociação_(%Meta)',
                               'Qtd. Venda','meta_vendas_ganhas','Qtd.Venda_GAP','Qtd.Venda_GAP_(%Meta)','Valor Venda',
                               'meta_valor_vendas_ganhas','Valor Venda_GAP','Valor Venda_(%Meta)']]
        df_venda['Ticket Médio'] = df_venda['Valor Venda']/df_venda['Qtd. Venda']

        df_posvenda = df_master[['semana','proposta_posvenda',
                               'meta_posvenda_proposta','Proposta PosVenda_GAP','Proposta PosVenda_(%Meta)','negociacao_posvenda',
                               'meta_posvenda_negociações','Negociação PosVenda_GAP','Negociação PosVenda_(%Meta)','Qtd. PosVenda',
                               'meta_posvendas_negócios_ganhos','Qtd. PosVenda_GAP','Qtd. PosVenda_(%Meta)','Valor PosVenda',
                                 'meta_posvenda_valor_vendas','Valor PosVenda_GAP','Valor PosVenda_(%Meta)']]
        df_posvenda['Ticket Médio'] = df_posvenda['Valor PosVenda']/df_posvenda['Qtd. PosVenda']

        df_vendaepos = df_master[['semana','Proposta (Venda+Pos)','meta_Proposta (Venda+Pos)',
                               'Proposta (Venda+Pos)_GAP','Proposta (Venda+Pos)_(%Meta)','Negociação (Venda+Pos)','meta_Negociação (Venda+Pos)','Negociação (Venda+Pos)_GAP',
                               'Negociação (Venda+Pos)_(%Meta)','Qtd. Venda (Venda+Pos)','meta_Qtd. Venda (Venda+Pos)','Qtd. Venda (Venda+Pos)_GAP','Qtd. Venda (Venda+Pos)_(%Meta)',
                               'Valor Venda (Venda+Pos)','meta_Valor Venda (Venda+Pos)','Valor Venda (Venda+Pos)_GAP','Valor Venda (Venda+Pos)_(%Meta)']]
        df_vendaepos['Ticket Médio'] = df_vendaepos['Valor Venda (Venda+Pos)']/df_vendaepos['Qtd. Venda (Venda+Pos)']


        st.title("VISÃO GERAL")

        col1,col2,col3 = st.columns([3,3,3])

        fig = go.Figure(go.Indicator(
            mode = "number+gauge+delta",
            number={'prefix': "R$ ", 'valueformat': ".2f"},
            value=df_vendaepos['Valor Venda (Venda+Pos)'].sum(),
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': df_vendaepos['meta_Valor Venda (Venda+Pos)'].sum()},
            title={'text': "Valor em Negócios Ganhos"}))

        col1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+gauge+delta",
            value=df_vendaepos['Qtd. Venda (Venda+Pos)'].sum(),
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': df_vendaepos['meta_Qtd. Venda (Venda+Pos)'].sum()},
            title={'text': "Número de Negócios Ganhos"}))

        col2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+gauge+delta",
            number={'prefix': "R$ ", 'valueformat': ".2f"},
            value=df_vendaepos['Valor Venda (Venda+Pos)'].sum()/df_vendaepos['Qtd. Venda (Venda+Pos)'].sum(),
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': df_vendaepos['meta_Valor Venda (Venda+Pos)'].sum()/df_vendaepos['meta_Qtd. Venda (Venda+Pos)'].sum()},
            title={'text': "Ticket Médio"}))

        col3.plotly_chart(fig, use_container_width=True)

        propposvendas = df_posvenda['proposta_posvenda'].sum()
        negposvendas = df_posvenda['negociacao_posvenda'].sum()
        posvendas = df_posvenda['Qtd. PosVenda'].sum()
        vendaposvendas = df_posvenda['Valor PosVenda'].sum()
        vendas = df_venda['Qtd. Venda'].sum()
        valorvendas = df_venda['Valor Venda'].sum()
        propvendas = df_venda['Proposta'].sum()
        negvendas = df_venda['Negociação'].sum()
        leadsqualificados = df_prevenda['Leads Qualificados'].sum()
        qualificacoes = df_prevenda['Qualificação'].sum()
        leads = df_prevenda['Leads'].sum()

        col1,col2 = st.columns([6,3])

        fig = go.Figure(go.Funnel(
            y=['Leads','Qualificações','Leads Qualificados','Propostas','Negociações','Qtd.Vendas'],
            x=[leads,qualificacoes,leadsqualificados,propvendas,negvendas,vendas],
            textposition="inside",
            textinfo="value+percent previous",
            opacity=0.80, marker={"color": ["deepskyblue", "lightsalmon", "tan", "teal", "silver","white"],
                                    "line": {"width": [4, 2, 2, 3, 1, 1],
                                            "color": ["white", "wheat", "blue", "wheat", "white", "green"]}},
            connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}})
        )
        fig.update_layout(margin=dict(t=0))

        col1.plotly_chart(fig, use_container_width=True)

        valorvendas_formatado = "R${:,.2f}".format(valorvendas).replace(",", "X").replace(".", ",").replace("X", ".")
        col1.subheader(f'Valor de Vendas: {valorvendas_formatado}')

        fig = go.Figure(go.Funnel(
            y=['Proposta_PosVenda','Negociação_PosVenda','Qtd.PosVenda'],
            x=[propposvendas,negposvendas,posvendas],
            textinfo="value+percent previous",
            textposition="inside",
            opacity=0.80, marker={"color": ["lightblue", "tan", "teal", "teal", "silver", "white"],
                                  "line": {"width": [4, 2, 2, 3, 1, 1],
                                           "color": ["white", "wheat", "blue", "wheat", "white", "green"]}},
            connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}})
        )
        fig.update_layout(margin=dict(t=0))
        col2.plotly_chart(fig, use_container_width=True)

        valorposvendas_formatado = "R${:,.2f}".format(vendaposvendas).replace(",", "X").replace(".", ",").replace("X", ".")
        col2.subheader(f'Valor de PosVendas: {valorposvendas_formatado}')


        st.divider()

        st.title("PRÉ-VENDA")
        col1, col2, col3 = st.columns([2,2,2])
        container1 = col1.container(height = 360, border=False)
        container2 = col2.container(height=360, border=False)
        container3 = col3.container(height=360, border=False)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_prevenda['Leads'].sum(),
            delta={"reference": df_prevenda['meta_leads'].sum(), "valueformat": ".0f"},
            title={"text": "Leads Recebidos"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))


        fig.update_layout(paper_bgcolor="#025E73", height=345)

        fig.update_layout(xaxis={'range': [0, 62]})

        fig.update_layout(margin=dict(t=0))

        container1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_prevenda['Qualificação'].sum(),
            delta={"reference": df_prevenda['meta_qualificações'].sum(), "valueformat": ".0f"},
            title={"text": "Qualificações Realizadas"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#025E73", height=345)

        fig.update_layout(margin=dict(t=0))

        container2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_prevenda['Leads Qualificados'].sum(),
            delta={"reference": df_prevenda['meta_leads_qualificados'].sum(), "valueformat": ".0f"},
            title={"text": "Leads Qualificados"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#025E73", height=345)

        fig.update_layout(margin=dict(t=0))

        container3.plotly_chart(fig, use_container_width=True)

        seletor_prevenda = st.selectbox("Selecione o indicador para acompanhar a evolução semanal:",["Leads","Qualificação","Leads Qualificados"])
        if seletor_prevenda == "Leads":
            meta_prevenda = "meta_leads"
        if seletor_prevenda == "Qualificação":
            meta_prevenda = "meta_qualificações"
        if seletor_prevenda == "Leads Qualificados":
            meta_prevenda = "meta_leads_qualificados"

        # Dados do gráfico de linha
        x_line = df_prevenda['semana']
        y_line = df_prevenda[seletor_prevenda]
        y_line2 = df_prevenda[meta_prevenda]

        fig = px.line(df_prevenda, x=x_line, y=y_line, labels=f'{seletor_prevenda}')
        fig.add_trace(go.Scatter(x=x_line, y=y_line2, mode='lines', name = f"{meta_prevenda}"))

        st.plotly_chart(fig, use_container_width=True)

        def highlight_prevenda(s):
            return ['background-color: #026873' if s.name in ['Leads', 'meta_leads','Lead_(%Meta)','Lead_GAP'] else 'background-color: #025E73' if s.name in ['Qualificação', 'meta_qualificações','Qualificação_(%Meta)','Qualificação_GAP'] else 'background-color: #011F26' if s.name in ['Leads Qualificados', 'meta_leads_qualificados','Leads Qualificados_(%Meta)','Leads Qualificados_GAP'] else '' for v in s]

        st.dataframe(df_prevenda.style.apply(highlight_prevenda, axis=0).format({'Lead_(%Meta)': '{:.2%}','Qualificação_(%Meta)': '{:.2%}','Leads Qualificados_(%Meta)': '{:.2%}'}), hide_index=True, use_container_width=True)

        st.divider()

        st.title("VENDA")

        col1, col2, col3,col4 = st.columns([2, 2, 2,2])
        container1 = col1.container(height=360, border=False)
        container2 = col2.container(height=360, border=False)
        container3 = col3.container(height=360, border=False)
        container4 = col4.container(height=360, border=False)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_venda['Proposta'].sum(),
            delta={"reference": df_venda['meta_propostas'].sum(), "valueformat": ".0f"},
            title={"text": "Propostas Realizadas"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#73B351", height=345)

        fig.update_layout(xaxis={'range': [0, 62]})

        fig.update_layout(margin=dict(t=0))

        container1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_venda['Negociação'].sum(),
            delta={"reference": df_venda['meta_negociações'].sum(), "valueformat": ".0f"},
            title={"text": "Negociações Realizadas"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#73B351", height=345)

        fig.update_layout(margin=dict(t=0))

        container2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_venda['Qtd. Venda'].sum(),
            delta={"reference": df_venda['meta_vendas_ganhas'].sum(), "valueformat": ".0f"},
            title={"text": "Vendas Ganhas"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#73B351", height=345)

        fig.update_layout(margin=dict(t=0))

        container3.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_venda['Valor Venda'].sum(),
            delta={"reference": df_venda['meta_valor_vendas_ganhas'].sum(), "valueformat": ".0f"},
            title={"text": "Valor Vendas"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#1D241E", height=345)

        fig.update_layout(margin=dict(t=0))

        container4.plotly_chart(fig, use_container_width=True)

        seletor_venda = st.selectbox("Selecione o indicador para acompanhar a evolução semanal:",
                                        ["Proposta", "Negociação", "Qtd. Venda","Valor Venda"])
        if seletor_venda == "Proposta":
            meta_venda = "meta_propostas"
        if seletor_venda == "Negociação":
            meta_venda = "meta_negociações"
        if seletor_venda == "Qtd. Venda":
            meta_venda = "meta_vendas_ganhas"
        if seletor_venda == "Valor Venda":
            meta_venda = "meta_valor_vendas_ganhas"

        # Dados do gráfico de linha
        x_line = df_venda['semana']
        y_line = df_venda[seletor_venda]
        y_line2 = df_venda[meta_venda]


        fig = px.line(df_venda, x=x_line, y=y_line)
        fig.add_trace(go.Scatter(x=x_line, y=y_line2, mode='lines', name=f'{seletor_venda}'))

        st.plotly_chart(fig, use_container_width=True)

        def highlight_venda(s):
            return ['background-color: #73B351' if s.name in ['Proposta', 'meta_propostas','Proposta_(%Meta)','Proposta_GAP'] else 'background-color: #284026' if s.name in ['Negociação', 'meta_negociações','Negociação_(%Meta)','Negociação_GAP'] else 'background-color: #1D241E' if s.name in ['Qtd. Venda', 'meta_vendas_ganhas','Qtd.Venda_GAP','Qtd.Venda_GAP_(%Meta)'] else '' for v in s]

        st.dataframe(df_venda.style.apply(highlight_venda, axis=0).format({'Proposta_(%Meta)': '{:.2%}','Negociação_(%Meta)': '{:.2%}','Qtd.Venda_GAP_(%Meta)': '{:.2%}','Valor Venda_(%Meta)': '{:.2%}','Valor Venda': 'R$ {:,.2f}','meta_valor_vendas_ganhas': 'R$ {:,.2f}','Valor Venda_GAP': 'R$ {:,.2f}','Ticket Médio': 'R$ {:,.2f}'}),use_container_width=True, hide_index=True)

        st.divider()

        st.title("PÓS-VENDA")

        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        container1 = col1.container(height=360, border=False)
        container2 = col2.container(height=360, border=False)
        container3 = col3.container(height=360, border=False)
        container4 = col4.container(height=360, border=False)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_posvenda['proposta_posvenda'].sum(),
            delta={"reference": df_posvenda['meta_posvenda_proposta'].sum(), "valueformat": ".0f"},
            title={"text": "Propostas Pós-Venda"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#7F7F3F", height=345)

        fig.update_layout(xaxis={'range': [0, 62]})

        fig.update_layout(margin=dict(t=0))

        container1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_posvenda['negociacao_posvenda'].sum(),
            delta={"reference": df_posvenda['meta_posvenda_negociações'].sum(), "valueformat": ".0f"},
            title={"text": "Negociações Pós-Venda"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#7F7F3F", height=345)

        fig.update_layout(margin=dict(t=0))

        container2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_posvenda['Qtd. PosVenda'].sum(),
            delta={"reference": df_posvenda['meta_posvendas_negócios_ganhos'].sum(), "valueformat": ".0f"},
            title={"text": "Pós-Vendas Ganhas"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#7F7F3F", height=345)

        fig.update_layout(margin=dict(t=0))

        container3.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_posvenda['Valor PosVenda'].sum(),
            delta={"reference": df_posvenda['meta_posvenda_valor_vendas'].sum(), "valueformat": ".0f"},
            title={"text": "Valor Vendas Pós-Venda"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#1F1F0F", height=345)

        fig.update_layout(margin=dict(t=0))

        container4.plotly_chart(fig, use_container_width=True)

        seletor_posvenda = st.selectbox("Selecione o indicador para acompanhar a evolução semanal:",
                                     ["proposta_posvenda", "negociacao_posvenda", "Qtd. PosVenda", "Valor PosVenda"])

        if  seletor_posvenda == "proposta_posvenda":
            meta_posvenda = "meta_posvenda_proposta"
        if  seletor_posvenda == "negociacao_posvenda":
            meta_posvenda = "meta_posvenda_negociações"
        if  seletor_posvenda == "Qtd. PosVenda":
            meta_posvenda = "meta_posvendas_negócios_ganhos"
        if  seletor_posvenda == "Valor PosVenda":
            meta_posvenda = "meta_posvenda_valor_vendas"

        # Dados do gráfico de linha
        x_line = df_posvenda['semana']
        y_line = df_posvenda[seletor_posvenda]
        y_line2 = df_posvenda[meta_posvenda]


        fig = px.line(df_posvenda, x=x_line, y=y_line)
        fig.add_trace(go.Scatter(x=x_line, y=y_line2, mode='lines', name=f'{seletor_posvenda}'))

        st.plotly_chart(fig, use_container_width=True)

        def highlight_venda(s):
            return ['background-color: #7F7F3F' if s.name in ['proposta_posvenda', 'meta_posvenda_proposta','Proposta PosVenda_(%Meta)','Proposta PosVenda_GAP'] else 'background-color: #3F3F1F' if s.name in ['negociacao_posvenda', 'meta_posvenda_negociações','Negociação PosVenda_(%Meta)','Negociação PosVenda_GAP'] else 'background-color: #1F1F0F' if s.name in ['Qtd. PosVenda', 'meta_posvendas_negócios_ganhos','Qtd. PosVenda_GAP','Qtd. PosVenda_(%Meta)'] else '' for v in s]

        st.dataframe(df_posvenda.style.apply(highlight_venda, axis=0).format({'Proposta PosVenda_(%Meta)': '{:.2%}','Negociação PosVenda_(%Meta)': '{:.2%}','Qtd. PosVenda_(%Meta)': '{:.2%}','Valor PosVenda_(%Meta)': '{:.2%}','Valor PosVenda': 'R$ {:,.2f}','meta_posvenda_valor_vendas': 'R$ {:,.2f}','Valor PosVenda_GAP': 'R$ {:,.2f}','Ticket Médio': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)

        st.divider()

        st.title("VENDA + PÓS-VENDA")

        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        container1 = col1.container(height=360, border=False)
        container2 = col2.container(height=360, border=False)
        container3 = col3.container(height=360, border=False)
        container4 = col4.container(height=360, border=False)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_vendaepos['Proposta (Venda+Pos)'].sum(),
            delta={"reference": df_vendaepos['meta_Proposta (Venda+Pos)'].sum(), "valueformat": ".0f"},
            title={"text": "Propostas (Venda+Pós)"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#8F1D2C", height=345)

        fig.update_layout(xaxis={'range': [0, 62]})

        fig.update_layout(margin=dict(t=0))

        container1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_vendaepos['Negociação (Venda+Pos)'].sum(),
            delta={"reference": df_vendaepos['meta_Negociação (Venda+Pos)'].sum(), "valueformat": ".0f"},
            title={"text": "Negociações (Venda+Pós)"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#8F1D2C", height=345)

        fig.update_layout(margin=dict(t=0))

        container2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_vendaepos['Qtd. Venda (Venda+Pos)'].sum(),
            delta={"reference": df_vendaepos['meta_Qtd. Venda (Venda+Pos)'].sum(), "valueformat": ".0f"},
            title={"text": "Pós-Vendas Ganhas"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#8F1D2C", height=345)

        fig.update_layout(margin=dict(t=0))

        container3.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_vendaepos['Valor Venda (Venda+Pos)'].sum(),
            delta={"reference": df_vendaepos['meta_Valor Venda (Venda+Pos)'].sum(), "valueformat": ".0f"},
            title={"text": "Valor Vendas Pós-Venda"},
            domain={'y': [0, 0.70], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="#400D2A", height=345)

        fig.update_layout(margin=dict(t=0))

        container4.plotly_chart(fig, use_container_width=True)

        seletor_vendaepos = st.selectbox("Selecione o indicador para acompanhar a evolução semanal:",
                                        ["Proposta (Venda+Pos)", "Negociação (Venda+Pos)", "Qtd. Venda (Venda+Pos)",
                                         "Valor Venda (Venda+Pos)"])

        if seletor_vendaepos == "Proposta (Venda+Pos)":
            meta_vendaepos = "meta_Proposta (Venda+Pos)"
        if seletor_vendaepos == "Negociação (Venda+Pos)":
            meta_vendaepos = "meta_Negociação (Venda+Pos)"
        if seletor_vendaepos == "Qtd. Venda (Venda+Pos)":
            meta_vendaepos = "meta_Qtd. Venda (Venda+Pos)"
        if seletor_vendaepos == "Valor Venda (Venda+Pos)":
            meta_vendaepos = "meta_Valor Venda (Venda+Pos)"

        # Dados do gráfico de linha
        x_line = df_vendaepos['semana']
        y_line = df_vendaepos[seletor_vendaepos]
        y_line2 = df_vendaepos[meta_vendaepos]


        fig = px.line(df_vendaepos, x=x_line, y=y_line)

        fig = px.line(df_vendaepos, x=x_line, y=y_line)
        fig.add_trace(go.Scatter(x=x_line, y=y_line2, mode='lines', name=f'{seletor_vendaepos}'))

        st.plotly_chart(fig, use_container_width=True)

        def highlight_venda(s):
            return ['background-color: #8F1D2C' if s.name in ['Proposta (Venda+Pos)', 'meta_Proposta (Venda+Pos)','Proposta (Venda+Pos)_(%Meta)','Proposta (Venda+Pos)_GAP'] else 'background-color: #5A142A' if s.name in ['Negociação (Venda+Pos)', 'meta_Negociação (Venda+Pos)','Negociação (Venda+Pos)_(%Meta)','Negociação (Venda+Pos)_GAP'] else 'background-color: #400D2A' if s.name in ['Qtd. Venda (Venda+Pos)', 'meta_Qtd. Venda (Venda+Pos)','Qtd. Venda (Venda+Pos)_GAP','Qtd. Venda (Venda+Pos)_(%Meta)'] else '' for v in s]

        st.dataframe(df_vendaepos.style.apply(highlight_venda, axis=0).format({'Proposta (Venda+Pos)_(%Meta)': '{:.2%}','Negociação (Venda+Pos)_(%Meta)': '{:.2%}','Qtd. Venda (Venda+Pos)_(%Meta)': '{:.2%}','Valor Venda (Venda+Pos)_(%Meta)': '{:.2%}','Valor Venda (Venda+Pos))': 'R$ {:,.2f}','meta_Valor Venda (Venda+Pos)': 'R$ {:,.2f}','Valor Venda (Venda+Pos)_GAP': 'R$ {:,.2f}','Ticket Médio': 'R$ {:,.2f}'}), use_container_width=True, hide_index=True)
    else:
        pass



if __name__ == '__main__':
    main()
