import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data



def converte_csv(df):
    return df.to_csv(index=False).encode('utf-8') #encode('utf-8') é utilizado para o texto não ficar ruim, ficar exatamente como é em português

def mensagem_sucesso():
    sucesso = st.sucesso('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()




st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url) #faz a requisição 
dados = pd.DataFrame.from_dict(response.json()) #transformando o json que foi carregado para um data Frame
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') #transformação da coluna data de compara para o formato Datetime


#filtro 

with st.expander('Colunas'):   
    colunas = st.multiselect('Selecione as colunas', list(dados.columns),list(dados.columns))
    

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos',dados['Produto'].unique(),dados['Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço',0,5000,(0,5000)) #(0,5000) Essa tupla significa que usamos um valor máximo e um mínimo como valor padrão

with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione a data',(dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Categoria do produto'):
    categoria_produto = st.multiselect('Selecione a categoria do produto',dados['Categoria do Produto'].unique(),dados['Categoria do Produto'].unique())

with st.sidebar.expander('Frete de venda'):
    frete = st.slider('Frete', 0,250,(0,250))

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Vendedor', dados['Vendedor'].unique(),dados['Vendedor'].unique())

with st.sidebar.expander('Local de compra'):
    local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação da compra'):
    avaliacao_compra = st.slider('Selecione a avaliação da compra', 1,5,(1,5))

with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))


query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria_produto and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao_compra[0]<= `Avaliação da compra` <= @avaliacao_compra[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

dados_filtrados = dados.query(query)


dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    
    nome_arquivo = st.text_input('',label_visibility='collapsed', value= 'dados') #o valor por padrão será dados, já ficará escrito dados ali
    nome_arquivo += '.csv'
    

with coluna2:
    st.download_button('Fazer o download da tabela em csv', data=converte_csv(dados_filtrados),file_name=nome_arquivo,mime='text/csv', on_click=mensagem_sucesso)

