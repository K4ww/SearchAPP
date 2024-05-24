
from dash import html, dcc
import plotly.graph_objs as go
import dash


dash.register_page(__name__, path='/Collections')





layout = html.Div(html.Div(id='collections',children=[
         
        html.A(id='loginlogout', href='#',style={'background-color':'#007FA2','padding':15,'border-radius':20,'text-decoration':'none',
                                         'color':'white','position':'absolute','top':30,'left':'150%'}),
        dcc.Input(id="newcollectionname",placeholder="Entrez le nom de collection",style={'position':'relative','color':'white','background-color':'transparent','margin-left':'5%' }),
        html.Button("Ajouter collection",id="ajoutercollection",style={'position':'relative','margin-left':'2%'  }),
        html.Div(className='vl',style={'top':'5%'}),
        html.Ul(id='Mycollections'),
        dcc.Download(id="download-text")
    ]))



