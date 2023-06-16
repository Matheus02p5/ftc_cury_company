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

def TopEntregadores(df1, asc ):
    
    """ Função que lista os top 10 entregadores por tipo de cidade, utilizando o modo de crescente/decrescente (ascending = True/False).
    
    Input : Dataframe
    Output : Dataframe
    
    """

    df2 = (df1.loc[:, ["Delivery_person_ID", 'City', 'Time_taken(min)']]
              .groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending = asc ).reset_index())

    df1_aux01 = df2.loc[df2['City'] == "Metropolitian", :].head(10)
    df1_aux02 = df2.loc[df2['City'] == "Semi-Urban", :].head(10)
    df1_aux03 = df2.loc[df2['City'] == "Urban", :].head(10)

    df3=pd.concat ( [df1_aux01, df1_aux02, df1_aux03] ).reset_index(drop=True)
                    
    return df3

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

st.set_page_config(page_title='Visão Entregadores',page_icon='🛵',layout="wide")

st.header( 'Visão da Entregadores'  )

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
#Visão Entregadores
#------------------------------------------------

tab1, tab2 = st.tabs(['Visão Gerencial','_'])

with tab1:
     with st.container():
        st.title('Métricas Gerais')
                
        col1, col2, col3, col4 = st.columns(4, gap='large')
            
        with col1:
            maior = df1.loc[:, "Delivery_person_Age"].max()
            col1.metric( 'A maior idade', maior)
                  
        with col2:
            menor = df1.loc[:, "Delivery_person_Age"].min()
            col2.metric( 'A menor idade', menor)     
            
        with col3:
            melhor = df1.loc[:, "Vehicle_condition"].max()
            col3.metric( 'A melhor condição', melhor)     
                
        with col4:
            pior = df1.loc[:, "Vehicle_condition"].min()
            col4.metric( 'A pior condição', pior)       
                      
        st.markdown ("""---""")                
                
        with st.container():
            st.title('Avaliações')
            col1, col2 = st.columns([1.8,1.7], gap='small') 
            
            with col1:    
                st.markdown('##### avaliação média por entregador.')
                a = df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby(['Delivery_person_ID']).mean().reset_index()
                st.dataframe(a, width=600, height=565)
                
            with col2:    
                st.markdown('##### Avaliações por tipo de tráfego.')
                a = (df1.loc[:, ['Road_traffic_density','Delivery_person_Ratings']].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings': ['mean','std']}))
                
                a.columns = ['mean', 'std']
            
                a=a.reset_index()
                
                st.dataframe(a, width=400, height=250)
                
                st.markdown('##### Avaliações por condições climáticas')
                
                a = df1.loc[:, ['Weatherconditions','Delivery_person_Ratings']].groupby(['Weatherconditions']).agg({"Delivery_person_Ratings": ["mean", "std"]})

                #.agg serve para criar colunas com duas ordens diferentes, porém gera multi index
                a.columns = ["mean",'std']

                a=a.reset_index()
                st.dataframe(a, width=400, height=250)
                
                
        st.markdown ("""---""")                
                
        with st.container():
            st.title('Avaliações')
                
            col1, col2 = st.columns([5,5])
            
            with col1: 
                st.markdown('##### Os 10 entregadores mais rápidos por cidade.')
                
                df3 = TopEntregadores(df1, asc = True)
                st.dataframe(df3, width=800, height=600)
                    
            with col2:
                
                st.markdown('##### Os 10 entregadores mais lentos por cidade.')
                
                df3 = TopEntregadores(df1, asc = False)
                st.dataframe(df3, width=700, height=600 )