import streamlit as st
from PIL import Image


st.set_page_config(page_title='Home',page_icon='🏠',layout="wide")

#------------------------------------------------
#Sidebar
#------------------------------------------------
#image_path = 'logo.png'

image = Image.open( 'logo.png' )

st.sidebar.image( image, width=100)

st.sidebar.markdown ( '# Cury Company' )

st.sidebar.markdown ( '## Faster Delivery in Town' )

st.sidebar.markdown ("""---""")

st.sidebar.markdown('#### Powered by Matheus Pinheiro')

#==================================================================================================
#layout Streamlit
#==================================================================================================

st.write('# Cury Company Growth Dashboard')

st.markdown(""" 
           Dashboard desenvolvido para visualização dos indicadores e métricas de crescimento da empresa, analisando os entregadores e retaurantes.
           ### Índice de navegação:

            - Visão empresa: 
                - Visão Gerencial : Métrica gerais.
                - Visão Tática: Indicadores de crescimento Semanal.
                - Visão Geográfica: Indicadores de Insights Geográficos.                
            - Visão Entregadores: 
                - Acompanhamento de crescimento dos entregadores.      
            - Visão Restaurantes:
                - Acompanhamento de crescimento dos Resturantes.
            ### Contato para ajuda:
                - 📧  Matheussouzads@icloud.com
            """)