import requests
import pandas as pd
import streamlit as st
import json
import ast
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import numpy as np


@st.cache_data
def importar_dados(API):
    df = pd.read_csv('calendario.csv')
    df_metas = pd.read_csv('metas.csv')
    df_calendario = df.drop(['bin'], axis=1)
    df_calendario['period_start'] = pd.to_datetime(df_calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    df_calendario['period_end'] = pd.to_datetime(df_calendario['period_end'], format="%d/%m/%Y %H:%M:%S")

    # Configurações básicas
    api_key = API
    base_url = "https://api.pipedrive.com/v1/deals/collection"

    header = {
            "accept": "application/json",
    }

    # Parâmetros da requisição
    params = {
        "api_token": api_key,
        }

    # Faz a requisição GET
    response = requests.get(base_url, params=params, headers=header)

        # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Processa a resposta
        collection = response.json()
        df_collection = pd.DataFrame(collection['data'])
        df_collection = df_collection.drop(['id','pipeline_id','visible_to','title','status','creator_user_id','person_id','org_id','currency','add_time','probability','lost_reason','close_time','won_time'], axis=1)
        df_collection = df_collection.drop(['lost_time','expected_close_date','label','d37e324b28c7f29a3d719d583b59c8a4f223cfa8','c5b6580d582f1523f0a7f35d6f57e2cc5f2509b1','3cf0006761813cecfbe37d770bc8e2e86af7ce71','77b659d8902f3058f432d31eb4d785d0060abb32','ec4a83d46625568e6a20809120c8713c3135d02d','0d9b666e5b83b6c6e387367fa6be18d3c59ba2ea','65d876eef576d197dd57a928cd0e1c34474e47aa','c8c5bbeaf3f9df2fec79f64e778f3dd459865d95','205d940b74611d0a70732261f89e7307a303e4f7','42916f6dc6aed4986fc366c73d0a18d0a23e76ea','b8e1342fb544f446ffe233d7a551f131d0238106','927ed92972eb6e360a7b7f649889c5c2424693ec','333ce5cc0379b10f96d3e07024b75dd218f5df80'], axis=1)

        etapas_mapping = {
            1: "Lead",
            2: "Lead",
            3: "Lead",
            4: "Lead",
            5: "Lead",
            6: "Qualificação",
            7: "Lead Qualificado",
            8: "Lead Qualificado",
            9: "Proposta",
            10: "Negociação",
            11: "Venda Ganha",
            12: "Venda Ganha",
            13: "Venda Ganha",
            14: "Pós-Venda Proposta",
            15: "Pós-Venda Negociação",
            16: "Pós-Venda Ganha",
        }
        df_collection['etapa'] = df_collection['stage_id'].map(etapas_mapping)
        df_collection = df_collection.groupby(['user_id', 'update_time', 'etapa']).agg({'value': 'sum', 'stage_id':'count'}).reset_index()
        df_collection['update_time'] = pd.to_datetime(df_collection['update_time'])
        df_collection['user_id'] = df_collection['user_id'].astype(str)



        df_bins = df.drop(['period_start', 'period_end', 'semana'], axis=1)
        df_bins['bin'] = pd.to_datetime(df_bins['bin'])

        bins = df_bins['bin'].tolist()
        labels = ["semana 1","semana 2","semana 3","semana 4","semana 5","semana 6","semana 7","semana 8","semana 9",
                  "semana 10","semana 11","semana 12","semana 13","semana 14","semana 15","semana 16","semana 17",
                  "semana 18","semana 19","semana 20","semana 21","semana 22","semana 23","semana 24"]

        df_collection['semana'] = pd.cut(df_collection['update_time'], bins=bins, labels=labels)

        df_collection = df_collection.drop(['update_time'], axis=1)
        df_collection_total = df_collection.drop(['user_id'], axis=1)
        df_collection_total = df_collection_total.groupby(['semana', 'etapa']).agg(
            {'value': 'sum', 'stage_id': 'count'}).reset_index()
        df_collection = df_collection.groupby(['user_id','semana', 'etapa']).agg({'value': 'sum', 'stage_id':'count'}).reset_index()
        df_collection = pd.merge(df_collection, df, on='semana')
        df_collection = df_collection[['user_id','period_start','period_end','semana','etapa','value','stage_id']]
        df_collection['qtd.'] = df_collection['stage_id']
        df_collection = df_collection.drop(['stage_id'], axis=1)


        # Transformando a coluna 'Estágio' em várias colunas usando pivot_table
        df_collectionv = df_collection.pivot_table(index=['user_id','period_start', 'period_end', 'semana'], columns='etapa', values=['value', 'qtd.'], fill_value=0)


        # Para achatar o MultiIndex nas colunas (opcional)
        df_collectionv.columns = ['_'.join(col).strip() for col in df_collectionv.columns.values]


        # Resetando o índice para tornar 'Data Inicial', 'Data Final' e 'Semana' novamente em colunas
        df_collectionv.reset_index(inplace=True)
        df_metas['user_id'] = df_metas['user_id'].astype(str)
        df_collectionv = pd.merge(df_collectionv, df_metas, on=['semana', 'user_id'])

        colunas = ['qtd._Lead','qtd._Qualificação','Qtd._Lead Qualificado','qtd._Proposta','qtd._Negociação','qtd._Venda Ganha',
                   'qtd._Pós-Venda Proposta','qtd._Pós-Venda Negociação','qtd._Pós-Venda Ganha','value_Lead','value_Qualificação',
                   'value_Lead Qualificado','value_Proposta','value_Negociação','value_Venda Ganha','value_Pós-Venda Proposta',
                   'value_Pós-Venda Negociação','value_Pós-Venda Ganha','meta_leads','meta_qualificações','meta_leads_qualificados',
                   'meta_propostas','meta_negociações','meta_vendas_ganhas','meta_valor_vendas_ganhas','meta_posvenda_proposta',
                   'meta_posvenda_negociações','meta_posvendas_negócios_ganhos','meta_posvenda_valor_vendas']

        colunas_prevenda = ['qtd._Lead','qtd._Qualificação','Qtd._Lead Qualificado','value_Lead','value_Qualificação',
                            'value_Lead Qualificado','meta_leads','meta_qualificações','meta_leads_qualificados']
        colunas_venda = ['qtd._Proposta','qtd._Negociação','qtd._Venda Ganha','value_Proposta','value_Negociação','value_Venda Ganha','meta_propostas',
                         'meta_negociações','meta_vendas_ganhas','meta_valor_vendas_ganhas']
        colunas_posvenda = ['qtd._Pós-Venda Proposta','qtd._Pós-Venda Negociação','qtd._Pós-Venda Ganha','value_Pós-Venda Proposta',
                            'value_Pós-Venda Negociação','value_Pós-Venda Ganha','meta_posvenda_proposta',
                            'meta_posvenda_negociações','meta_posvendas_negócios_ganhos','meta_posvenda_valor_vendas']

        for i in colunas:
           if i not in df_collectionv.columns:
                # Se não existir, cria a coluna com todos os valores igual a 0
                df_collectionv[i] = 0

        df_prevenda = df_collectionv.drop(colunas_venda, axis=1)
        df_prevenda = df_prevenda.drop(colunas_posvenda, axis=1)
        df_prevenda = df_prevenda.drop(['value_Lead','value_Lead Qualificado','value_Qualificação'], axis=1)
        df_prevenda = df_prevenda[['user_id','period_start','period_end','semana','qtd._Lead','meta_leads','qtd._Qualificação','meta_qualificações','qtd._Lead Qualificado','meta_leads_qualificados']]
        df_prevenda['period_start'] = pd.to_datetime(df_prevenda['period_start'], dayfirst=True)
        df_prevenda['period_end'] = pd.to_datetime(df_prevenda['period_end'], dayfirst=True)
        df_prevenda = df_prevenda.sort_values(by=['period_start','user_id'])

        df_venda = df_collectionv.drop(colunas_prevenda, axis=1)
        df_venda = df_venda.drop(colunas_posvenda, axis=1)
        df_venda = df_venda.drop(['value_Proposta', 'value_Negociação'], axis=1)
        df_venda = df_venda[
            ['user_id', 'period_start', 'period_end', 'semana', 'qtd._Proposta','meta_propostas', 'qtd._Negociação',
             'meta_negociações', 'qtd._Venda Ganha','meta_vendas_ganhas', 'value_Venda Ganha','meta_valor_vendas_ganhas']]
        df_venda['period_start'] = pd.to_datetime(df_venda['period_start'], dayfirst=True)
        df_venda['period_end'] = pd.to_datetime(df_venda['period_end'], dayfirst=True)
        df_venda = df_venda.sort_values(by=['period_start','user_id'])

        df_posvenda = df_collectionv.drop(colunas_prevenda, axis=1)
        df_posvenda = df_posvenda.drop(colunas_venda, axis=1)
        df_posvenda = df_posvenda.drop(['value_Pós-Venda Negociação', 'value_Pós-Venda Proposta'], axis=1)
        df_posvenda = df_posvenda[['user_id', 'period_start', 'period_end', 'semana', 'qtd._Pós-Venda Proposta', 'meta_posvenda_proposta', 'qtd._Pós-Venda Negociação','meta_posvenda_negociações', 'qtd._Pós-Venda Ganha','meta_posvendas_negócios_ganhos', 'value_Pós-Venda Ganha','meta_posvenda_valor_vendas']]
        df_posvenda['period_start'] = pd.to_datetime(df_posvenda['period_start'], dayfirst=True)
        df_posvenda['period_end'] = pd.to_datetime(df_posvenda['period_end'], dayfirst=True)
        df_posvenda = df_posvenda.sort_values(by=['period_start','user_id'])

        df_vendaepos = df_venda
        df_vendaepos = df_vendaepos.drop(['meta_propostas','qtd._Negociação','qtd._Proposta','meta_negociações','qtd._Venda Ganha','meta_vendas_ganhas','value_Venda Ganha','meta_valor_vendas_ganhas'], axis=1)
        df_vendaepos['proposta (venda+pos)'] = df_collectionv['qtd._Proposta']+df_collectionv['qtd._Pós-Venda Proposta']
        df_vendaepos['meta_proposta (venda+pos)'] = df_collectionv['meta_propostas']+df_collectionv['meta_posvenda_proposta']
        df_vendaepos['negociação (venda+pos)'] = df_collectionv['qtd._Negociação']+df_collectionv['qtd._Pós-Venda Negociação']
        df_vendaepos['meta_negociação (venda+pos)'] = df_collectionv['meta_negociações'] + df_collectionv['meta_posvenda_negociações']
        df_vendaepos['venda (venda+pos)'] = df_collectionv['qtd._Venda Ganha'] + df_collectionv['qtd._Pós-Venda Ganha']
        df_vendaepos['meta_venda (venda+pos)'] = df_collectionv['meta_vendas_ganhas'] + df_collectionv['meta_posvendas_negócios_ganhos']
        df_vendaepos['valor_venda (venda+pos)'] = df_collectionv['value_Venda Ganha'] + df_collectionv['value_Pós-Venda Ganha']
        df_vendaepos['meta_valor_venda (venda+pos)'] = df_collectionv['meta_valor_vendas_ganhas'] + df_collectionv['meta_posvenda_valor_vendas']

    else:
        print(f"Erro na requisição: {response.status_code}, Resposta: {response.text}")

    return df_collectionv,df_prevenda,df_venda,df_posvenda,df_vendaepos

def main():
    #Configuração página inicial
    st.set_page_config(page_title='Dashboard', layout= 'wide', initial_sidebar_state='collapsed')


    API = st.text_input('API:')

    if API:

        df_collectionv, df_prevenda, df_venda, df_posvenda, df_vendaepos = importar_dados(API)

        sidebar = st.sidebar
        sidebar.header("FILTRO DE USUÁRIO")
        user = sidebar.selectbox("Escolha o usuário",["Agregado", "Todos"] + list(df_collectionv['user_id'].unique()))



        if user == "Agregado":
            df_prevenda = df_prevenda.drop(['user_id'], axis=1)
            df_prevenda = df_prevenda.groupby('period_start', as_index=False).agg({
                'period_end': 'first',
                'semana': 'first',
                'qtd._Lead': 'sum',
                'meta_leads': 'sum',
                'qtd._Qualificação': 'sum',
                'meta_qualificações': 'sum',
                'qtd._Lead Qualificado': 'sum',
                'meta_leads_qualificados': 'sum',
            })
            df_venda = df_venda.drop(['user_id'], axis=1)
            df_venda = df_venda.groupby('period_start', as_index=False).agg({
                'period_end': 'first',
                'semana': 'first',
                'qtd._Proposta': 'sum',
                'meta_propostas': 'sum',
                'qtd._Negociação': 'sum',
                'meta_negociações': 'sum',
                'qtd._Venda Ganha': 'sum',
                'meta_vendas_ganhas': 'sum',
                'value_Venda Ganha': 'sum',
                'meta_valor_vendas_ganhas': 'sum',
            })
            df_posvenda = df_posvenda.drop(['user_id'], axis=1)
            df_posvenda = df_posvenda.groupby('period_start', as_index=False).agg({
                'period_end': 'first',
                'semana': 'first',
                'qtd._Pós-Venda Proposta': 'sum',
                'meta_posvenda_proposta': 'sum',
                'qtd._Pós-Venda Negociação': 'sum',
                'meta_posvenda_negociações': 'sum',
                'qtd._Pós-Venda Ganha': 'sum',
                'meta_posvendas_negócios_ganhos': 'sum',
                'value_Pós-Venda Ganha': 'sum',
                'meta_posvenda_valor_vendas': 'sum',
            })
            df_vendaepos = df_vendaepos.drop(['user_id'], axis=1)
            df_vendaepos = df_vendaepos.groupby('period_start', as_index=False).agg({
                'period_end': 'first',
                'semana': 'first',
                'proposta (venda+pos)': 'sum',
                'meta_proposta (venda+pos)': 'sum',
                'negociação (venda+pos)': 'sum',
                'meta_negociação (venda+pos)': 'sum',
                'venda (venda+pos)': 'sum',
                'meta_venda (venda+pos)': 'sum',
                'valor_venda (venda+pos)': 'sum',
                'meta_valor_venda (venda+pos)': 'sum',
            })
        else:
            if user == "Todos":
                controle = 1
            else:
                df_prevenda = df_prevenda[df_prevenda['user_id']==user]
                df_venda = df_venda[df_venda['user_id']==user]
                df_posvenda = df_posvenda[df_posvenda['user_id']==user]
                df_vendaepos = df_vendaepos[df_vendaepos['user_id']==user]


        st.title("VISÃO GERAL")

        col1,col2,col3 = st.columns([3,3,3])

        fig = go.Figure(go.Indicator(
            mode = "number+gauge+delta",
            value=df_vendaepos['valor_venda (venda+pos)'].sum(),
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': df_vendaepos['meta_valor_venda (venda+pos)'].sum()},
            title={'text': "Faturamento"}))

        col1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+gauge+delta",
            value=df_vendaepos['venda (venda+pos)'].sum(),
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': df_vendaepos['meta_venda (venda+pos)'].sum()},
            title={'text': "Qtd. Vendas"}))

        col2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+gauge+delta",
            value=df_vendaepos['valor_venda (venda+pos)'].sum()/df_vendaepos['venda (venda+pos)'].sum(),
            domain={'x': [0, 1], 'y': [0, 1]},
            delta={'reference': df_vendaepos['meta_valor_venda (venda+pos)'].sum()/df_vendaepos['meta_venda (venda+pos)'].sum()},
            title={'text': "Ticket Médio"}))

        col3.plotly_chart(fig, use_container_width=True)

        posvendas = df_posvenda['qtd._Pós-Venda Ganha'].sum()
        negposvendas = df_posvenda['qtd._Pós-Venda Negociação'].sum()
        vendas = df_venda['qtd._Venda Ganha'].sum()
        negvendas = df_venda['qtd._Negociação'].sum()
        leadsqualificados = df_prevenda['qtd._Lead Qualificado'].sum()
        leads = df_prevenda['qtd._Lead'].sum()


        fig = go.Figure(go.Funnel(
            y=["Pós-Vendas", "Negociações Pós-Vendas", "Vendas", "Negociações Vendas", "Leads Qualificados","Leads"],
            x=[posvendas,negposvendas,vendas,negvendas,leadsqualificados,leads],
            textposition="inside",
            opacity=0.80, marker={"color": ["deepskyblue", "lightsalmon", "tan", "teal", "silver","white"],
                                  "line": {"width": [4, 2, 2, 3, 1, 1],
                                           "color": ["white", "wheat", "blue", "wheat", "white", "green"]}},
            connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}})
        )
        fig.update_layout(margin=dict(t=0))

        st.plotly_chart(fig, use_container_width=True)


        st.divider()

        st.title("PRÉ-VENDA")
        col1, col2, col3 = st.columns([2,2,2])
        container1 = col1.container(height = 350, border=False)
        container2 = col2.container(height=350, border=False)
        container3 = col3.container(height=350, border=False)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_prevenda['qtd._Lead'].sum(),
            delta={"reference": df_prevenda['meta_leads'].sum(), "valueformat": ".0f"},
            title={"text": "Leads"},
            domain={'y': [0, 1], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="blue")

        fig.update_layout(xaxis={'range': [0, 62]})

        fig.update_layout(margin=dict(t=0))

        container1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_prevenda['qtd._Qualificação'].sum(),
            delta={"reference": df_prevenda['meta_qualificações'].sum(), "valueformat": ".0f"},
            title={"text": "Qualificações"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="blue")

        fig.update_layout(margin=dict(t=0))

        container2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_prevenda['qtd._Lead Qualificado'].sum(),
            delta={"reference": df_prevenda['meta_leads_qualificados'].sum(), "valueformat": ".0f"},
            title={"text": "Leads Qualificados"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="blue")

        fig.update_layout(margin=dict(t=0))

        container3.plotly_chart(fig, use_container_width=True)

        seletor_prevenda = st.selectbox("Escolha a dimensão de prevenda:",["qtd._Lead","qtd._Qualificação","qtd._Lead Qualificado"])
        if seletor_prevenda == "qtd._Lead":
            meta_prevenda = "meta_leads"
        if seletor_prevenda == "qtd._Qualificação":
            meta_prevenda = "meta_qualificações"
        if seletor_prevenda == "qtd._Lead Qualificado":
            meta_prevenda = "meta_leads_qualificados"

        # Dados do gráfico de linha
        x_line = df_prevenda['semana']
        y_line = df_prevenda[seletor_prevenda]
        y_line2 = df_prevenda[meta_prevenda]

        if user == "Agregado":
            fig = px.line(df_prevenda, x=x_line, y=y_line)
        else:
            fig = px.line(df_prevenda, x=x_line, y=y_line, color='user_id')
        fig.add_trace(go.Scatter(x=x_line, y=y_line2, mode='lines', name='Meta Leads'))

        st.plotly_chart(fig, use_container_width=True)

        def highlight_prevenda(s):
            return ['background-color: darkblue' if s.name in ['meta_leads', 'meta_qualificações','meta_leads_qualificados'] else '' for v in s]

        st.dataframe(df_prevenda.style.apply(highlight_prevenda, axis=0), hide_index=True, use_container_width=True)

        st.divider()

        st.title("VENDA")

        col1, col2, col3,col4 = st.columns([2, 2, 2,2])
        container1 = col1.container(height=350, border=False)
        container2 = col2.container(height=350, border=False)
        container3 = col3.container(height=350, border=False)
        container4 = col4.container(height=350, border=False)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_venda['qtd._Proposta'].sum(),
            delta={"reference": df_venda['meta_propostas'].sum(), "valueformat": ".0f"},
            title={"text": "Propostas"},
            domain={'y': [0, 1], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="green")

        fig.update_layout(xaxis={'range': [0, 62]})

        fig.update_layout(margin=dict(t=0))

        container1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_venda['qtd._Negociação'].sum(),
            delta={"reference": df_venda['meta_negociações'].sum(), "valueformat": ".0f"},
            title={"text": "Negociações"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="green")

        fig.update_layout(margin=dict(t=0))

        container2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_venda['qtd._Venda Ganha'].sum(),
            delta={"reference": df_venda['meta_vendas_ganhas'].sum(), "valueformat": ".0f"},
            title={"text": "Vendas Ganhas"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="green")

        fig.update_layout(margin=dict(t=0))

        container3.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_venda['value_Venda Ganha'].sum(),
            delta={"reference": df_venda['meta_valor_vendas_ganhas'].sum(), "valueformat": ".0f"},
            title={"text": "Valor Vendas"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="purple")

        fig.update_layout(margin=dict(t=0))

        container4.plotly_chart(fig, use_container_width=True)

        seletor_venda = st.selectbox("Escolha a dimensão de venda:",
                                        ["qtd._Proposta", "qtd._Negociação", "qtd._Venda Ganha","value_Venda Ganha"])
        if seletor_venda == "qtd._Proposta":
            meta_venda = "meta_propostas"
        if seletor_venda == "qtd._Negociação":
            meta_venda = "meta_negociações"
        if seletor_venda == "qtd._Venda Ganha":
            meta_venda = "meta_vendas_ganhas"
        if seletor_venda == "value_Venda Ganha":
            meta_venda = "meta_valor_vendas_ganhas"

        # Dados do gráfico de linha
        x_line = df_venda['semana']
        y_line = df_venda[seletor_venda]
        y_line2 = df_venda[meta_venda]

        if user == "Agregado":
            fig = px.line(df_venda, x=x_line, y=y_line)
        else:
            fig = px.line(df_venda, x=x_line, y=y_line, color='user_id')

        fig.add_trace(go.Scatter(x=x_line, y=y_line2, mode='lines', name='Meta'))

        st.plotly_chart(fig, use_container_width=True)

        def highlight_venda(s):
            return ['background-color: darkblue' if s.name in ['meta_propostas', 'meta_negociações',
                                                                 'meta_vendas_ganhas', 'meta_valor_vendas_ganhas'] else '' for v in s]

        st.dataframe(df_venda.style.apply(highlight_venda, axis=0),use_container_width=True, hide_index=True)

        st.divider()

        st.title("PÓS-VENDA")

        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        container1 = col1.container(height=350, border=False)
        container2 = col2.container(height=350, border=False)
        container3 = col3.container(height=350, border=False)
        container4 = col4.container(height=350, border=False)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_posvenda['qtd._Pós-Venda Proposta'].sum(),
            delta={"reference": df_posvenda['meta_posvenda_proposta'].sum(), "valueformat": ".0f"},
            title={"text": "Propostas Pós-Venda"},
            domain={'y': [0, 1], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="brown")

        fig.update_layout(xaxis={'range': [0, 62]})

        fig.update_layout(margin=dict(t=0))

        container1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_posvenda['qtd._Pós-Venda Negociação'].sum(),
            delta={"reference": df_posvenda['meta_posvenda_negociações'].sum(), "valueformat": ".0f"},
            title={"text": "Negociações Pós-Venda"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="brown")

        fig.update_layout(margin=dict(t=0))

        container2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_posvenda['qtd._Pós-Venda Ganha'].sum(),
            delta={"reference": df_posvenda['meta_posvendas_negócios_ganhos'].sum(), "valueformat": ".0f"},
            title={"text": "Pós-Vendas Ganhas"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="brown")

        fig.update_layout(margin=dict(t=0))

        container3.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_posvenda['value_Pós-Venda Ganha'].sum(),
            delta={"reference": df_posvenda['meta_posvenda_valor_vendas'].sum(), "valueformat": ".0f"},
            title={"text": "Valor Vendas Pós-Venda"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="blue")

        fig.update_layout(margin=dict(t=0))

        container4.plotly_chart(fig, use_container_width=True)

        seletor_posvenda = st.selectbox("Escolha a dimensão de pós-venda:",
                                     ["qtd._Pós-Venda Proposta", "qtd._Pós-Venda Negociação", "qtd._Pós-Venda Ganha", "value_Pós-Venda Ganha"])

        if  seletor_posvenda == "qtd._Pós-Venda Proposta":
            meta_posvenda = "meta_posvenda_proposta"
        if  seletor_posvenda == "qtd._Pós-Venda Negociação":
            meta_posvenda = "meta_posvenda_negociações"
        if  seletor_posvenda == "qtd._Pós-Venda Ganha":
            meta_posvenda = "meta_posvendas_negócios_ganhos"
        if  seletor_posvenda == "value_Pós-Venda Ganha":
            meta_posvenda = "meta_posvenda_valor_vendas"

        # Dados do gráfico de linha
        x_line = df_posvenda['semana']
        y_line = df_posvenda[seletor_posvenda]
        y_line2 = df_posvenda[meta_posvenda]

        if user == "Agregado":
            fig = px.line(df_posvenda, x=x_line, y=y_line)
        else:
            fig = px.line(df_posvenda, x=x_line, y=y_line, color='user_id')

        fig.add_trace(go.Scatter(x=x_line, y=y_line2, mode='lines', name='Meta'))

        st.plotly_chart(fig, use_container_width=True)

        def highlight_venda(s):
            return ['background-color: darkblue' if s.name in ['meta_posvenda_proposta', 'meta_posvenda_negociações',
                                                                 'meta_posvendas_negócios_ganhos', 'meta_posvenda_valor_vendas'] else ''
                    for v in s]

        st.dataframe(df_posvenda.style.apply(highlight_venda, axis=0), use_container_width=True, hide_index=True)

        st.divider()

        st.title("VENDA + PÓS-VENDA")

        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        container1 = col1.container(height=350, border=False)
        container2 = col2.container(height=350, border=False)
        container3 = col3.container(height=350, border=False)
        container4 = col4.container(height=350, border=False)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_vendaepos['proposta (venda+pos)'].sum(),
            delta={"reference": df_vendaepos['meta_proposta (venda+pos)'].sum(), "valueformat": ".0f"},
            title={"text": "Propostas (Venda+Pós)"},
            domain={'y': [0, 1], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="darkgreen")

        fig.update_layout(xaxis={'range': [0, 62]})

        fig.update_layout(margin=dict(t=0))

        container1.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_vendaepos['negociação (venda+pos)'].sum(),
            delta={"reference": df_vendaepos['meta_negociação (venda+pos)'].sum(), "valueformat": ".0f"},
            title={"text": "Negociações (Venda+Pós)"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="darkgreen")

        fig.update_layout(margin=dict(t=0))

        container2.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_vendaepos['venda (venda+pos)'].sum(),
            delta={"reference": df_vendaepos['meta_venda (venda+pos)'].sum(), "valueformat": ".0f"},
            title={"text": "Pós-Vendas Ganhas"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="darkgreen")

        fig.update_layout(margin=dict(t=0))

        container3.plotly_chart(fig, use_container_width=True)

        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=df_vendaepos['valor_venda (venda+pos)'].sum(),
            delta={"reference": df_vendaepos['meta_valor_venda (venda+pos)'].sum(), "valueformat": ".0f"},
            title={"text": "Valor Vendas Pós-Venda"},
            domain={'y': [1, 0.75], 'x': [0.25, 0.75]}))

        fig.update_layout(paper_bgcolor="darkred")

        fig.update_layout(margin=dict(t=0))

        container4.plotly_chart(fig, use_container_width=True)

        seletor_vendaepos = st.selectbox("Escolha a dimensão de venda+pós:",
                                        ["proposta (venda+pos)", "negociação (venda+pos)", "venda (venda+pos)",
                                         "valor_venda (venda+pos)"])

        if seletor_vendaepos == "proposta (venda+pos)":
            meta_vendaepos = "meta_proposta (venda+pos)"
        if seletor_vendaepos == "negociação (venda+pos)":
            meta_vendaepos = "meta_negociação (venda+pos)"
        if seletor_vendaepos == "venda (venda+pos)":
            meta_vendaepos = "meta_venda (venda+pos)"
        if seletor_vendaepos == "valor_venda (venda+pos)":
            meta_vendaepos = "meta_valor_venda (venda+pos)"

        # Dados do gráfico de linha
        x_line = df_vendaepos['semana']
        y_line = df_vendaepos[seletor_vendaepos]
        y_line2 = df_vendaepos[meta_vendaepos]

        if user == "Agregado":
            fig = px.line(df_vendaepos, x=x_line, y=y_line)
        else:
            fig = px.line(df_vendaepos, x=x_line, y=y_line, color='user_id')
        fig.add_trace(go.Scatter(x=x_line, y=y_line2, mode='lines', name='Meta'))

        st.plotly_chart(fig, use_container_width=True)

        def highlight_venda(s):
            return ['background-color: darkblue' if s.name in ['meta_proposta (venda+pos)', 'meta_negociação (venda+pos)',
                                                                 'meta_venda (venda+pos)',
                                                                 'meta_valor_venda (venda+pos)'] else ''
                    for v in s]

        st.dataframe(df_vendaepos.style.apply(highlight_venda, axis=0), use_container_width=True, hide_index=True)



if __name__ == '__main__':
    main()
