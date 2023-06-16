# Importação Bibliotecas

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
import datetime as dt
import folium
from PIL import Image
from streamlit_folium import folium_static

#------------------------------------------------
#Funções
#------------------------------------------------

def clean_code( df1 ):
    
    """ Função de limpeza de dataframe
    
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção do espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo. (remoção dos texto da variável numérica.
        
        Input : Dataframe
        Output : Dataframe
        
    """
    #1 Convertendo a Coluna de Delivery_person_Age para inteiro (Int)

    linhas_selecionadas = df1['Delivery_person_Age'] != "NaN " #Retirando as linhas com itens nulos
    df1 = df1.loc[linhas_selecionadas, :].copy() #Guardando as informações utilizadas
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int ) #Convertendo para inteiro.

    #2 convertendo a coluna de Delivery_person_Ratings para decimal ( Float )
    df1["Delivery_person_Ratings"] = df1['Delivery_person_Ratings'].astype( float )

    #3 convertendo a coluna de Order_Date para data ( pandas.to_datetime )
    df1['Order_Date'] = pd.to_datetime ( df1['Order_Date'], format= '%d-%m-%Y' )

    #4 convertando multiple_deliveries para numeros inteiros ( Int ) e retirandos os valores Nulos "NaN "

    linhas_selecionadas = df1['multiple_deliveries'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    linhas_selecionadas = df1['City'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Weatherconditions'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Festival'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = df1['Time_Orderd'] != "NaN "
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #5 resetando o index 

    df1 = df1.reset_index( drop=True )

    #6 for i in range ( len (df1 ) ):

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip() # .strip comando em dataframe que retira os espaços

    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()

    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()

    df1.loc[:, "Type_of_vehicle"] = df1.loc[:, 'Type_of_vehicle'].str.strip()

    df1.loc[:, "City"] = df1.loc[:, "City"].str.strip()

    df1.loc[:, "Delivery_person_ID"] = df1.loc[:, "Delivery_person_ID"].str.strip()                                                                      

    df1.loc[:, "Festival"] = df1.loc[:, "Festival"].str.strip()                                                                      

    #7 Limpando o Time_taken(min)                                        
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1

def PedidosPorDia(df1):
    """ Gera um gráfico de barras com os pedidos diarios utilizando as colunas do dataframe
        
        Input : Dataframe
        Output : Plotly bar.gráfic 
    """

    i = ['ID', 'Order_Date']
 #Seleção de linhas
    grafico = df1.loc[:,i].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(grafico, x= 'Order_Date', y= 'ID')
    return fig

def PedidosPorTrafego(df1):
    """ Gera um gráfico de pizza com os pedidos diarios utilizando as colunas do dataframe
        
        Input : Dataframe
        Output : Plotly pie.gráfic 
    """
    i = df1.loc[:, ['ID', "Road_traffic_density"]].groupby(['Road_traffic_density']).count().reset_index()
    i['perc_entregas'] = i['ID'] / i['ID'].sum()
    fig = px.pie(i , values="perc_entregas", names="Road_traffic_density")
    return fig

def PedidosPorTrafegoDaCidade(df1):
    """ Gera um gráfico de bolhas com os pedidos diarios utilizando as colunas do dataframe
        
        Input : Dataframe
        Output : Plotly scartter.gráfic
    """
    i = df1.loc[:, ["ID", "City", "Road_traffic_density"]].groupby(["City","Road_traffic_density"]).count().reset_index()
    fig = px.scatter(i, x='City', y='Road_traffic_density', size = "ID", color = 'City') 
    return fig 

def PedidosSemanais(df1):
    """ Gera um gráfico de linhas com os pedidos semanais utilizando as colunas do dataframe
        
        Input : Dataframe
        Output : Plotly line.gráfic
    """
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' ) #dt converte Type "Series". strftime tranforma de data utilizando a mascara "%U$ para o formato semana 
    i = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    fig=px.line( i, x='week_of_year', y="ID")
    return fig

def PedidosSemanaisPorEntregador(df1):
    """ Gera um gráfico de linhas utilizando a quantidade de pedidos por semana divididos pela quantidade de entregadores unicos por semana
        
        Input : Dataframe
        Output : Plotly line.gráfic
    
    """
    i = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    j = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()

    #pd.merge comando para juntar dois df's 
    l = pd.merge( i, j, how= 'inner')
    l['order_delivery'] = l['ID'] / l['Delivery_person_ID']

    fig = px.line(l, x='week_of_year', y= 'order_delivery')
    return fig


def MapaLocalizacaoMedia(df1):
    """ Gera um mapa das localizações utilizando as colunas de latitude e longitude média dos restaurantes. 
        
        Input : Dataframe
        Output : Folium Marker.Map
    
    """
    
    i = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map_ = folium.Map()

    for index, location_info in i.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
        
    folium_static(map_, width=700, height=450)
    
    return None


# -------------------------------------------------------------------- Inicio da estrutura do código ----------------------------------------------------------------------

# Importando dados
df = pd.read_csv('train.csv')

# Limpando dados
df1 = clean_code( df )

#------------------------------------------------
#Sidebar
#------------------------------------------------

st.set_page_config(page_title='Visão Empresa',page_icon='👨‍💼',layout="wide")

st.header( 'Visão da Empresa'  )

#image_path = 'logo.png'

image = Image.open( 'logo.png' )

st.sidebar.image( image, width=100)

st.sidebar.markdown ( '# Cury Company' )

st.sidebar.markdown ( '## Faster Delivery in Town' )

st.sidebar.markdown ("""---""")

st.sidebar.markdown ("## Seleciona a data limite:")

date_slider = st.sidebar.slider("Qual a data máxima ? :",
                  value=dt.datetime( 2022, 4, 13),
                  min_value=dt.datetime( 2022, 2, 11), 
                  max_value=dt.datetime( 2022, 4, 6),
                  format="DD-MM-YYYY")

st.sidebar.markdown ("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições de trânsito ? :' ,  ['Low', 'Medium', 'High',  'Jam'] , default=['Low', 'Medium', 'High',  'Jam'])

st.sidebar.markdown ("""---""")
st.sidebar.markdown('#### Powered by Matheus Pinheiro')

#FILTROS utilizando os comandos da sidebar
## Slider filtro
linhas_selecionadas = df1['Order_Date'] <= date_slider

df1 = df1.loc[linhas_selecionadas, :]

## Multiselect Filtro

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options)

df1 = df1.loc[linhas_selecionadas, :]

#==================================================================================================
#layout Streamlit
#==================================================================================================


#------------------------------------------------
#Visão empresa
#------------------------------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Pedidos por dia')
        
        fig = PedidosPorDia(df1)
        fig.update_layout( width=850, height=600)
        st.plotly_chart(fig, use_countainer_width=True)
        
    with st.container():
        st.title('Distribuição dos pedidos')
        st.markdown("""---""")

        col1, col2 = st.columns(2, gap='small')  
        st.markdown("""---""")

        with  col1 :            
            st.markdown('##### Por tipo de tráfego.')
            
            fig = PedidosPorTrafego(df1)
            fig.update_layout( width=400, height=400)
            st.plotly_chart(fig, use_countainer_width=True)
        
        with  col2 :
            st.markdown('##### Por cidade / tipo de tráfego.')
            
            fig = PedidosPorTrafegoDaCidade(df1)
            fig.update_layout( width=400, height=400)
            st.plotly_chart(fig, use_countainer_width=True)
            
with tab2:
    with st.container():
        st.markdown('# Pedidos semanais')
        
        fig = PedidosSemanais(df1)
        fig.update_layout( width=650, height=450)
        st.plotly_chart(fig, use_countainer_width=True)

    st.markdown ("""----""")
    with st.container():
        st.markdown('# Pedidos semanais por entregador ')
        
        fig = PedidosSemanaisPorEntregador(df1)
        fig.update_layout( width=650, height=450)
        st.plotly_chart(fig)
    
with tab3:
       with st.container(): 
            st.markdown('### Mapa com a localização média dos restaurantes. ')
            MapaLocalizacaoMedia(df1)
            
            st.markdown ("""----""")
            
            st.title('Visualizações:')
            st.markdown ('')
            st.markdown('##### 1. Análise de densidade.')
            st.write(' Ao visualizar o mapa com as localizações médias, é possível identificar áreas de alta densidade, onde há uma concentração significativa de clientes e restaurantes. Essas áreas podem indicar regiões mais movimentadas e com maior demanda por serviços de entrega.')
            st.markdown('##### 2. Otimização de rotas.')
            st.write('Com as localizações médias, é possível analisar a distribuição geográfica dos clientes em relação aos restaurantes. Essa informação pode ser utilizada para otimizar as rotas de entrega, minimizando distâncias percorridas e tempo de entrega. Algoritmos de roteirização podem ser aplicados para criar as melhores rotas possíveis.')
            st.markdown('##### 3. Identificação de áreas de baixa cobertura')
            st.write('Ao observar o mapa, pode-se identificar áreas com poucas localizações médias, o que indica uma possível baixa cobertura do serviço de delivery. Essas áreas podem representar oportunidades de expansão do negócio, com a adição de restaurantes parceiros ou ações de marketing direcionadas para atrair mais clientes nessas regiões.')
            st.markdown('##### 4. Segmentação de mercado')
            st.write('Com base nas localizações médias, é possível segmentar o mercado por região geográfica. Essa segmentação pode ser útil para direcionar campanhas promocionais específicas para determinadas áreas, levando em consideração as preferências e necessidades dos clientes em cada região.')
            st.markdown('##### 5. Análise de concorrência')
            st.write('Ao comparar as localizações médias dos restaurantes com os concorrentes diretos, é possível identificar padrões de concentração ou dispersão. Essa análise pode fornecer insights sobre a estratégia de posicionamento dos concorrentes e ajudar a identificar oportunidades para diferenciar o serviço de delivery.')
            