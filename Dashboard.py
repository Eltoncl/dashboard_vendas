import streamlit as st
import requests
import pandas as pd
import plotly.express as px

#configurações da página
st.set_page_config(layout='wide')




#formatando os números
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'    





st.title('DASHBOARD DE VENDAS :shopping_trolley:')

#acessando aos dados da loja 
url = 'https://labdados.com/produtos'

#criando uma lista para passarmos para o select box
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']


#criando a barra lateral que será aplicado para todas as abas
st.sidebar.title('Filtros')

#O primeiro parâmetro é uma label (explicação) do que é esse Selectbox.
#  Vamos inserir Região entre aspas. Como segundo parâmetro, vamos usar a lista regioes.
regiao = st.sidebar.selectbox('Região', regioes)
#precisamos fazer uma modificação porque a região "Brasil" não pode ser filtrada na API. Colocamos essa opção no Selectbox para a pessoa usuária não fazer nenhuma filtragem.
#Caso não queiramos fazer nenhuma filtragem, vamos inserir if regiao == "Brasil" seguido de dois-pontos e regiao igual a aspas vazias. 
# Ou seja, se a opção do selectbox for Brasil, não faremos nenhuma filtragem e manteremos a URL padrão.
if regiao == 'Brasil':
    regiao = ''


#filtro dos anos
todos_anos = st.sidebar.checkbox('Dados de todo o período',value=True) #value=True porque por padrão ele carregará já marcado
if todos_anos: #se ano estiver marcado, não farei filtragem
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020,2023)


query_string = {'região':regiao.lower(), 'ano':ano}
#Vamos criar a variável query_string que vai ser igual ao dicionário. A primeira chave vai ser regiao que colocamos na URL e também passamos o valor regiao.lower().
#Como criamos a lista de valores com as regiões escritas com a primeira letra em maiúscula para ficar visualmente mais fácil para a pessoa usuária fazer a seleção, 
# mas a API só aceita valores em letras minúsculas. Por isso, passamos o lower() para deixar a região de forma correta na URL.
#A segunda chave do dicionário será ano entre aspas, seguido de dois-pontos e ano. Dessa maneira, será identificado que o valor ano vai selecionar uma opção do slider.
#Agora precisamos passar essa variável query_string para dentro do requests.get().
#Após url de requests.get(), passamos um parâmetro que vai chamar para params igual à query_string.




#agora é preciso acessar os dados da API através do requests.get(),que recebe a url como argumento.
#response = requests.get(url) adicionaremos a query_string para dentro do requests
response = requests.get(url, params=query_string)


#Temos que transformar essa requisição para um JSON que será transformado em um DataFrame
dados = pd.DataFrame.from_dict(response.json())

#Alterar o formato da coluna de datas, que está como texto e precisa ser convertido para o formato dateTime 
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'],format = '%d/%m/%Y')
#vamos construir uma tabela para armazenar essas informações e, depois, utilizá-la para construir o gráfico.
#que será a receita mensal

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]






### Tabelas de Receita ###
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

#construir uma tabela para receita mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].sum().reset_index()
#pd.Grouper(freq='M')está agrupando pelos meses.
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### Tabelas de quantidade de vendas ###

vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))


### Tabelas vendedores ###
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count'])) #agg permite que se faça agregação de soma e de 
#contagem ao mesmo tempo
#faremos o gráfico diretamente na aba porque criamos um input de quantidade de vendedores 
# e o usaremos para criar o gráfico.




##Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template= 'seaborn',
                                  hover_name='Local da compra',
                                  hover_data= {'lat': False, 'lon': False}, #aqui removemos as informações de latitude e longitude
                                  title='Receita por Estado')


#Este gráfico possui a informação de preço no eixo y, mas queremos alterar o nome deste eixo. 
# Para isso, na linha seguinte, chamamos fig_receita_mensal.update_layout(), passando yaxis_title = 'Receita'. 
# Assim, estamos nomeando o eixo y como "Receita".
fig_receita_mensal = px.line(receita_mensal,
                            x= 'Mes',
                            y = 'Preço',
                            markers=True,
                            range_y= (0, receita_mensal.max()),
                            color='Ano',
                            line_dash='Ano',
                            title='Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita Mensal')


fig_receita_estados = px.bar(receita_estados.head(),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,
                            title='Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

#como nessa tabela só possui duas informações, não precisamos passar os eixos x e y
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title='Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')



fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')


##Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1: #permite colocarmos algo dentro das colunas
    #adicionando métrica
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita,use_container_width=True)  #use_container_width=True vai respeitar o tamanho da coluna
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de Vendas',formata_numero(dados.shape[0])) #O Shape me fornece a quantidade de linhas e de colunas, 
    #como precisamos da quantidade de linhas para saber o total de vendas, utilizo o shape[0]
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

    #st.dataframe(dados) não usaremos mais essa tabela

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores',2,10,5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(
            vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
            x='sum',
            y=vendedores[['sum']].sort_values(['sum'], ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (receita)'
            )
        st.plotly_chart(fig_receita_vendedores)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(
            vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
            x='count',
            y=vendedores[['count']].sort_values(['count'], ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)'
            )

        st.plotly_chart(fig_vendas_vendedores)