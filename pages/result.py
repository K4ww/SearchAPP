
from dash import html, dcc
import plotly.graph_objs as go
import dash


dash.register_page(__name__, path='/Result')





layout = html.Div(children=[
    html.Div(id='save-feedback'),
    dcc.Location(id='url', refresh=False),
    html.Div(id='FilterBar',className='FilterBar',children=[
            html.H1('Filtres'),
            dcc.Input(id='title',placeholder="Titre d'un blog"),
            dcc.Input(id='author',placeholder="Nom d'auteur"),
            dcc.Input(id='type',placeholder='Type'),
            html.Div(children=[html.Button("tes",id={"type":"collection","index":"1"}, n_clicks=0,style={'position':'relative','margin-top':'20px','display':'none'}),html.Button("tes",id={"type":"collection","index":2}, n_clicks=0,style={'position':'relative','margin-top':'20px'})],
        
        id='side-menu',style={'background-color':'white','width':'20%','height':'20%','position':'relative','display':'none'} # Start with the menu hidden
    ),
    ]),
    
    html.Div(className='vl'),
    html.Div(id='searchBar',children=[
        dcc.Input(id='InputResult',autoComplete='off',placeholder='Entrez votre recherche ici')
    ]),
    html.Div(id='loginAndInfo'),
    dcc.Loading(
            id="loading-1",
            type="default",
            color="white",
            children=[html.Div(id='results',children=[
        html.Div(id='ResultAnalyse',children=[
             html.Ul(children=[
                  html.Li(id='NumberOfResults',children='Numberofresults'),
                  html.Li(id='NumberOfAuthors',children='numberofauthors'),
                  html.Li(id='NumberOfLanguages',children='numberofcountries')
             ])
        ]),
        html.Ul(id='MyResults'),
    ]),
    html.A(id='loginlogout', href='#',style={'background-color':'#007FA2','padding':15,'border-radius':20,'text-decoration':'none',
                                         'color':'white','position':'absolute','top':30,'right':50}),
    html.A("mescollection",id='mescollections', href='/Collections'),
    html.Div(id='Statistics',children=[
          dcc.Graph(
        id='author-document-bar-graph',
        figure={
                'data': [],  # Placeholder for the initial figure
                'layout': go.Layout(
                    title='Nombre des documents par auteur',
                    xaxis={'title': 'Auteur'},
                    yaxis={'title': 'Nombre des documents'},
                )
            }),

            dcc.Graph(
        id='country-document-bar-graph',
        figure={
                'data': [],  # Placeholder for the initial figure
                'layout': go.Layout(
                    title='Nombre des documents par pays',
                    xaxis={'title': 'Pays'},
                    yaxis={'title': 'Nombre des documents'}
                )
            })
    
    ]),]
        ),
    
])



