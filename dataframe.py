import requests
import pandas as pd
import streamlit as st
import ast
from datetime import datetime, timedelta

def criar_deals_id(API):
    api_key = API
    base_url = "https://api.pipedrive.com/v1/deals"
    all_deals = []  # Lista para armazenar todos os deals

    header = {
        "accept": "application/json",
    }

    params = {
        "api_token": api_key,
        "limit": 100,  # Define o número máximo de resultados por página
        "start": 0     # Inicia na primeira página
    }

    while True:
        # Faz a requisição GET
        response = requests.get(base_url, params=params, headers=header)

        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            data = response.json()
            if data['data'] is not None:
                all_deals.extend(data['data'])  # Adiciona os resultados à lista de todos os deals

                # Verifica se há mais páginas
                more_items = data['additional_data']['pagination']['more_items_in_collection']
                if more_items:
                    #Atualiza o parâmetro 'start' para a próxima página
                    params['start'] += params['limit']
                else:
                    break  # Sai do loop se não houver mais páginas
            else:
                break  # Sai do loop se a resposta não contiver 'data'
        else:
            print(f"Erro na requisição: {response.status_code}, Resposta: {response.text}")
            break

    # Converte a lista de todos os deals em um DataFrame
    if all_deals:
        df_collection = pd.DataFrame(all_deals)
        df_collection['user_id'] = df_collection['user_id'].apply(lambda x: x['name'] if isinstance(x, dict) and 'name' in x else None)
    else:
        df_collection = pd.DataFrame()  # Cria um DataFrame vazio se não houver deals

    return df_collection

def criar_usuários(API):
    api_key = API
    base_url = "https://api.pipedrive.com/v1/users"

    header = {
        "accept": "application/json",
    }

    params = {
        "api_token": api_key,
    }

    response = requests.get(base_url, params=params, headers=header)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Erro na requisição: {response.status_code}, Resposta: {response.text}")

    if data:
        df_users = pd.DataFrame(data['data'])
        df_users = df_users[['id','name']]

    return df_users

def criar_dados(API, ids):
        df_stages = pd.DataFrame()
        array_api = ids['id'].values

        for i in array_api:

            api_key = API
            base_url = f"https://api.pipedrive.com/v1/deals/{i}"

            header = {
                "accept": "application/json",
            }

            # PARÂMETRO DE REQUISIÇÃO
            params = {
                "api_token": api_key,
            }

            # Faz a requisição GET
            response = requests.get(base_url, params=params, headers=header)

            # Verifica se a requisição foi bem-sucedida
            if response.status_code == 200:
                # Processa a resposta
                collection = response.json()
                df_deal = pd.DataFrame(collection['data'])
                df_deal = df_deal[['add_time', 'stay_in_pipeline_stages']]
                df_deal = df_deal.loc[['times_in_stages']]

                str_deal = str(df_deal['stay_in_pipeline_stages'].iloc[0])
                dicionario = ast.literal_eval(str_deal)
                df_deal_stages = pd.DataFrame([dicionario])
                df_deal_stages['id'] = i
                df_deal_stages['add_time'] = df_deal['add_time'].iloc[0]
                df_deal_stages['add_time'] = pd.to_datetime(df_deal_stages['add_time'])

                colunas = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
                           'add_time', 'id']

                for i in colunas:
                    if i not in df_deal_stages.columns:
                        df_deal_stages[i] = 0

                if df_deal_stages['1'].iloc[0] == 0:
                    df_deal_stages['Data 1 Inicial'] = "Não Existiu"
                    df_deal_stages['Data 1 Final'] = "Não Existiu"
                else:
                    df_deal_stages['Data 1 Inicial'] = df_deal_stages['add_time']
                    df_deal_stages['Data 1 Final'] = df_deal_stages['add_time'] + timedelta(
                        seconds=int(df_deal_stages['1']))

                array_colunas = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16']

                for i in array_colunas:
                    if df_deal_stages[i].iloc[0] == 0:
                        df_deal_stages[f'Data {i} Inicial'] = "Não Existiu"
                        df_deal_stages[f'Data {i} Final'] = "Não Existiu"
                    else:
                        ant = int(i) - 1
                        if df_deal_stages[f'Data {ant} Inicial'].iloc[0] == "Não Existiu":
                            df_deal_stages[f'Data {i} Inicial'] = df_deal_stages['add_time']
                            df_deal_stages[f'Data {i} Final'] = df_deal_stages['add_time'] + timedelta(
                                seconds=int(df_deal_stages[f'{i}'].iloc[0]))
                        else:
                            df_deal_stages[f'Data {i} Inicial'] = df_deal_stages[f'Data {ant} Final'] + timedelta(
                                seconds=int(1))
                            df_deal_stages[f'Data {i} Final'] = df_deal_stages[f'Data {ant} Final'] + timedelta(
                                seconds=int(df_deal_stages[f'{i}'].iloc[0]))

                df_deal_stages = df_deal_stages.drop(
                    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'], axis=1)
                df_stages = pd.concat([df_stages, df_deal_stages], ignore_index=True)

            else:
                print(f"Erro na requisição: {response.status_code}, Resposta: {response.text}")

        return df_stages

def criar_leads(df_calendario, df_data):


    valor_substituir = datetime(1900, 1, 1, 0, 0, 0)
    df_data.replace('Não Existiu', valor_substituir, inplace=True)

    df_calendario['period_start'] = pd.to_datetime(df_calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    df_calendario['period_end'] = pd.to_datetime(df_calendario['period_end'], format="%d/%m/%Y %H:%M:%S")
    df_data['Data 1 Inicial'] = pd.to_datetime(df_data['Data 1 Inicial'])
    df_data['Data 2 Inicial'] = pd.to_datetime(df_data['Data 2 Inicial'])

    def contar_leads1(row):
        return df_data[(df_data['Data 1 Inicial'] >= row['period_start']) & (
                    df_data['Data 1 Inicial'] <= row['period_end'])].shape[0]

    def contar_leads2(row):
        return df_data[(df_data['Data 2 Inicial'] >= row['period_start']) & (
                    df_data['Data 2 Inicial'] <= row['period_end'])].shape[0]

    # Aplicar a função e criar a nova coluna
    df_calendario['Leads1'] = df_calendario.apply(contar_leads1, axis=1)
    df_calendario['Leads2'] = df_calendario.apply(contar_leads2, axis=1)
    df_calendario['Leads'] = df_calendario['Leads1'] + df_calendario['Leads2']
    df_calendario = df_calendario.drop(['bin','Leads1','Leads2'], axis=1)
    return df_calendario

def criar_proposta_negociacoes_posvenda(df_calendario, df_data):

    valor_substituir = datetime(1900, 1, 1, 0, 0, 0)
    df_data.replace('Não Existiu', valor_substituir, inplace=True)

    df_calendario['period_start'] = pd.to_datetime(df_calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    df_calendario['period_end'] = pd.to_datetime(df_calendario['period_end'], format="%d/%m/%Y %H:%M:%S")
    df_data['Data 14 Inicial'] = pd.to_datetime(df_data['Data 14 Inicial'])
    df_data['Data 15 Inicial'] = pd.to_datetime(df_data['Data 15 Inicial'])

    def contar_leads1(row):
        return df_data[(df_data['Data 14 Inicial'] >= row['period_start']) & (
                    df_data['Data 14 Inicial'] <= row['period_end'])].shape[0]

    def contar_leads2(row):
        return df_data[(df_data['Data 15 Inicial'] >= row['period_start']) & (
                    df_data['Data 15 Inicial'] <= row['period_end'])].shape[0]

    # Aplicar a função e criar a nova coluna
    df_calendario['proposta_posvenda'] = df_calendario.apply(contar_leads1, axis=1)
    df_calendario['negociacao_posvenda'] = df_calendario.apply(contar_leads2, axis=1)
    return df_calendario

def criar_atividades(API):
    api_key = API
    base_url = "https://api.pipedrive.com/v1/activities/collection"
    all_activities = []

    header = {
        "accept": "application/json",
    }

    # PARÂMETRO DE REQUISIÇÃO
    params = {
        "api_token": api_key,
    }

    while True:
        response = requests.get(base_url, params=params, headers=header)

        if response.status_code == 200:
            collection = response.json()
            if collection is not None:
                all_activities.extend(collection['data'])
                more_itens = collection['additional_data']['next_cursor']
                if more_itens:
                    params['cursor'] = more_itens
                else:
                    break
            else:
                break
        else:
            print(f"Erro na requisição: {response.status_code}, Resposta: {response.text}")
            break

    if all_activities:
        df_atividades = pd.DataFrame(all_activities)
    else:
        df_atividades = pd.DataFrame()

    df_atividades = df_atividades[['done','type','subject','user_id','add_time','marked_as_done_time']]
    return df_atividades

def criar_qualificacao(atividades, calendario):
    atividades = atividades[atividades['type'] == 'qualificacao']
    atividades['marked_as_done_time'].fillna('1900-01-01 00:00:00', inplace=True)
    atividades['marked_as_done_time'] = pd.to_datetime(atividades['marked_as_done_time'])
    atividades['add_time'] = pd.to_datetime(atividades['add_time'])
    calendario['period_start'] = pd.to_datetime(calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    calendario['period_end'] = pd.to_datetime(calendario['period_end'], format="%d/%m/%Y %H:%M:%S")

    def contar_atividade(row):
        return atividades[(atividades['marked_as_done_time'] >= row['period_start']) & (
                atividades['marked_as_done_time'] <= row['period_end'])].shape[0]

    calendario['Qualificação'] = calendario.apply(contar_atividade, axis=1)
    qualificacao = calendario
    return qualificacao

def criar_leads_qualificados(atividades, calendario):
    atividades = atividades[(atividades['type'] == 'diagnostico')| (atividades['type'] == 'apresentacao')]
    atividades['marked_as_done_time'].fillna('1900-01-01 00:00:00', inplace=True)
    atividades['marked_as_done_time'] = pd.to_datetime(atividades['marked_as_done_time'])
    atividades['add_time'] = pd.to_datetime(atividades['add_time'])
    calendario['period_start'] = pd.to_datetime(calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    calendario['period_end'] = pd.to_datetime(calendario['period_end'], format="%d/%m/%Y %H:%M:%S")

    def contar_atividade(row):
        return atividades[(atividades['add_time'] >= row['period_start']) & (
                atividades['add_time'] <= row['period_end'])].shape[0]

    calendario['Leads Qualificados'] = calendario.apply(contar_atividade, axis=1)
    leads_qualificados = calendario
    return leads_qualificados

def criar_proposta_venda(atividades, calendario):
    atividades = atividades[(atividades['type'] == 'proposta') | (atividades['type'] == 'orcamento')]
    atividades['marked_as_done_time'].fillna('1900-01-01 00:00:00', inplace=True)
    atividades['marked_as_done_time'] = pd.to_datetime(atividades['marked_as_done_time'])
    atividades['add_time'] = pd.to_datetime(atividades['add_time'])
    calendario['period_start'] = pd.to_datetime(calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    calendario['period_end'] = pd.to_datetime(calendario['period_end'], format="%d/%m/%Y %H:%M:%S")

    def contar_atividade(row):
        return atividades[(atividades['marked_as_done_time'] >= row['period_start']) & (
                atividades['marked_as_done_time'] <= row['period_end'])].shape[0]

    calendario['Proposta'] = calendario.apply(contar_atividade, axis=1)
    proposta = calendario
    return proposta

def criar_negociacao_venda(atividades, calendario):
    atividades = atividades[atividades['type'] == 'negociacao']
    atividades['marked_as_done_time'].fillna('1900-01-01 00:00:00', inplace=True)
    atividades['marked_as_done_time'] = pd.to_datetime(atividades['marked_as_done_time'])
    atividades['add_time'] = pd.to_datetime(atividades['add_time'])
    calendario['period_start'] = pd.to_datetime(calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    calendario['period_end'] = pd.to_datetime(calendario['period_end'], format="%d/%m/%Y %H:%M:%S")

    def contar_atividade(row):
        return atividades[(atividades['marked_as_done_time'] >= row['period_start']) & (
                atividades['marked_as_done_time'] <= row['period_end'])].shape[0]

    calendario['Negociação'] = calendario.apply(contar_atividade, axis=1)
    negociacao = calendario
    return negociacao

def criar_vendas(deals, calendario):
    deals = deals[['id','first_won_time','won_time','value','status','pipeline_id']]
    deals = deals[deals['status']=='won']
    deals = deals[deals['pipeline_id']==2]
    deals['first_won_time'] = pd.to_datetime(deals['first_won_time'])
    calendario['period_start'] = pd.to_datetime(calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    calendario['period_end'] = pd.to_datetime(calendario['period_end'], format="%d/%m/%Y %H:%M:%S")

    def contar_atividade(row):
        return deals[(deals['first_won_time'] >= row['period_start']) & (
                deals['first_won_time'] <= row['period_end'])].shape[0]

    def somar_vendas(row):
        return deals[(deals['first_won_time'] >= row['period_start']) & (
                deals['first_won_time'] <= row['period_end'])]['value'].sum()

    calendario['Qtd. Venda'] = calendario.apply(contar_atividade, axis=1)
    calendario['Valor Venda'] = calendario.apply(somar_vendas, axis=1)
    qtd_venda = calendario
    return qtd_venda

def criar_posvendas(deals, calendario):
    deals = deals[['id','close_time','won_time','value','status','pipeline_id']]
    deals = deals[deals['status']=='won']
    deals = deals[deals['pipeline_id']==3]
    deals['close_time'] = pd.to_datetime(deals['close_time'])
    calendario['period_start'] = pd.to_datetime(calendario['period_start'], format="%d/%m/%Y %H:%M:%S")
    calendario['period_end'] = pd.to_datetime(calendario['period_end'], format="%d/%m/%Y %H:%M:%S")

    def contar_atividade(row):
        return deals[(deals['close_time'] >= row['period_start']) & (
                deals['close_time'] <= row['period_end'])].shape[0]

    def somar_vendas(row):
        return deals[(deals['close_time'] >= row['period_start']) & (
                deals['close_time'] <= row['period_end'])]['value'].sum()

    calendario['Qtd. PosVenda'] = calendario.apply(contar_atividade, axis=1)
    calendario['Valor PosVenda'] = calendario.apply(somar_vendas, axis=1)
    qtd_posvenda = calendario
    return qtd_posvenda

def main():
    #Configuração página inicial
    st.set_page_config(page_title='Dashboard', layout= 'wide', initial_sidebar_state='collapsed')

    df_deals = criar_deals_id("732dbe014babd4937bfd09d86bb15f8c599a55e7")
    #df_dados = criar_dados("775de349564737e4196e225ffcae6e5dca99ba98",df_deals_id)
    df_dados = pd.read_csv('dados2.csv')
    df_calendario = pd.read_csv('calendario.csv')
    df_atividades = criar_atividades("732dbe014babd4937bfd09d86bb15f8c599a55e7")


    df_master = criar_leads(df_calendario, df_dados)
    df_master = criar_qualificacao(df_atividades,df_calendario)
    df_master = criar_leads_qualificados(df_atividades,df_calendario)
    df_master = criar_proposta_venda(df_atividades,df_calendario)
    df_master = criar_negociacao_venda(df_atividades,df_calendario)
    df_master = criar_vendas(df_deals,df_calendario)
    df_master = criar_proposta_negociacoes_posvenda(df_calendario,df_dados)
    df_master = criar_posvendas(df_deals,df_calendario)
    df_users = criar_usuários("732dbe014babd4937bfd09d86bb15f8c599a55e7")
    df_deals_posvenda = df_deals[df_deals['status']=='won']
    df_deals_posvenda = df_deals_posvenda[df_deals_posvenda['pipeline_id']==3]



    st.dataframe(df_users)

    st.dataframe(df_deals)
    st.dataframe(df_atividades)
    st.dataframe(df_dados)
    st.dataframe(df_master)


if __name__ == '__main__':
    main()
