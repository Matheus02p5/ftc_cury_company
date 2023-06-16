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
import numpy as np

#------------------------------------------------
#Funções
#------------------------------------------------
def MediaDesvioTempo(df1, festival, op):
    """ Utiliza o dataframe para exibir o tempo médio e o desvio padrão de entrega quando tem festival.
    
    Input : DataFrame, op
            "avg_time" = Calcula o tempo médio
            "std_time" = Calcula o desvio padrão
    
    Output : DataFrame 
        
    """
    
    
    cols = [ "Time_taken(min)", "Festival"]
    df1_aux = df1.loc[:, cols].groupby('Festival').agg ( {'Time_taken(min)' : ["mean", "std"]} ) 

    df1_aux.columns = ["avg_time", "std_time"]
    df1_aux = df1_aux.reset_index()

    linhas_selecionadas = df1_aux['Festival'] == festival

    df1_aux = np.round(df1_aux.loc[linhas_selecionadas, op],2)
    return df1_aux




def distancia(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[0:, cols].apply( lambda x: 
                                          haversine(
                                              (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                              (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
    a = np.round(df1['distance'].mean(),2)

                
    return a


def MediaStdPedidoCidade(df1):
    
    """ Utiliza o dataframe para exibir o tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.
    
    Input : DataFrame 
    Output : DataFrame
    
    """
    cols = ['City', "Time_taken(min)", "Type_of_order"]

    df1_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg ( {'Time_taken(min)' : ["mean", "std"]} ) 

    df1_aux.columns = ["avg_time", "std_time"]

    df1_aux = df1_aux.reset_index()
    return df1_aux


def tempoMedioStdPorCidade(df1):
    """ Utiliza as colunas do dataframe para exibir o tempo médio e o desvio padrão de entrega por cidade utilizando a biblioteca plotly.graph_objects para
     gerar um gráfico de barras.
    
    Input : DataFrame 
    Output : plotly.graph_objects / Bar Figure
    
    """
   
    cols = ['City', "Time_taken(min)"]

    df1_aux = df1.loc[:, cols].groupby('City').agg ( {'Time_taken(min)' : ["mean", "std"]} ) 

    df1_aux.columns = ["avg_time", "std_time"]
    df1_aux = df1_aux.reset_index()

    fig = go.Figure()

    fig.add_trace( go.Bar( name = 'Control', 
                                       x = df1_aux['City'], 
                                       y= df1_aux['avg_time'], 
                                       error_y=dict( type='data', 
                                       array=df1_aux['std_time'] )))

    fig.update_layout(barmode = 'group')
    return fig

def distribuicaoTempo(df1):
    
    """ Utiliza as colunas do dataframe para exibir um gráfico de Sol mostrando a distribuição de tempo utilizando as cidades e as densidades de transito.
    
    Input : DataFrame 
    Output : plotly.graph_objects / Sun Figure
    
    """
    
    cols = ['City', "Time_taken(min)", "Road_traffic_density"]

    df1_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg ( {'Time_taken(min)' : ["mean", "std"]} ) 

    df1_aux.columns = ["avg_time", "std_time"]

    df1_aux = df1_aux.reset_index()

    fig = px.sunburst(df1_aux, path=['City', 'Road_traffic_density'],values='avg_time', 
                                  color='std_time', color_continuous_scale='RdBu',
                                  color_continuous_midpoint=np.average(df1_aux['std_time']))
    return fig

def TempoMedioPorCidadePizza(df1):
    """ Utiliza as colunas do dataframe para exibir um gráfico de pizza mostrando a distribuição média entre as distancias dos restaurantes.
    
    Input : DataFrame 
    Output : plotly.graph_objects / Pie Figure
    
    """
    
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

    df1['distance'] = df1.loc[0:, cols].apply( lambda x: 
                                      haversine(
                                          (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                          (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )

    a = df1.loc[:, ["City",'distance']].groupby('City').mean().reset_index()

    fig = go.Figure( data = [ go.Pie(labels = a['City'], values = a['distance'], pull=[0,0.1,0])])
    return fig

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

# Importação de dados
df = pd.read_csv('train.csv')

df1 = clean_code( df )

#------------------------------------------------
#Sidebar
#------------------------------------------------

st.set_page_config(page_title='Visão Restaurantes',page_icon='🍽️',layout="wide")

st.header( 'Visão da Restaurantes'  )

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

#------------------------------------------------
#layout Streamlit
#------------------------------------------------

tab1, tab2 = st.tabs(['Visão Gerencial','_'])

with tab1:
    st.title('Métricas Gerais')
    
#====================================================================================================================================   
#Containers de dados: 1
#====================================================================================================================================     

    with st.container():

        col1, col2, col3, col4,col5, col6 = st.columns(6)

        with col1:

            a = len (df1.loc[:, 'Delivery_person_ID'].unique() )

            col1.metric("Entregadores", a)

        with col2:
            a = distancia(df1)
            col2.metric("Distância média", a)
            
        with col3:
            df1_aux = MediaDesvioTempo(df1, 'Yes', "avg_time")
            col3.metric('Tempo médio', df1_aux)

        with col4:    
            df1_aux = MediaDesvioTempo(df1, 'Yes', "std_time")
            col4.metric('Desvio padrão', df1_aux)

        with col5:
            df1_aux = MediaDesvioTempo(df1, 'No', "avg_time")
            col5.metric('Tempo médio', df1_aux)
            
        with col6:
            df1_aux = MediaDesvioTempo(df1, 'No', "std_time")
            col6.metric('Desvio padrão', df1_aux)
            
        st.markdown("""---""")        
        
#===================================================================================================================================   
#Containers de dados: 2
#====================================================================================================================================    
    
    with st.container():
        col1, col2 = st.columns (2, gap='large')
        
        with col1:
            st.title('Tempo médio de entregas por cidade')
           
            fig = TempoMedioPorCidadePizza(df1)
            fig.update_layout( width=450, height=500)
            st.plotly_chart(fig)
        
        with col2:
            
            st.title('Distribuição de tempo') 
            
            fig = distribuicaoTempo(df1)
            fig.update_layout( width=375, height=650)
            st.plotly_chart(fig)
            
#====================================================================================================================================    
#Containers de dados: 3
#====================================================================================================================================    

    with st.container():   
        
        st.markdown("""---""") 
        st.title('Desvio de tempo') 
        col1, col2 = st.columns (2, gap='medium')
        with col1:
            st.markdown('### O tempo médio e o desvio padrão de entrega por cidade.')
            
            fig = tempoMedioStdPorCidade(df1)
            fig.update_layout( width=400, height=600)
            st.plotly_chart(fig)
        
        with col2:
            st.markdown('### O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.')
            
            df1_aux = MediaStdPedidoCidade(df1)
            st.dataframe(df1_aux,  width=450, height=460)
            