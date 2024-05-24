
import dash_mantine_components as dmc
import dash
from pymongo import MongoClient





from urllib.parse import quote
from dash import html, dcc
client = MongoClient("mongodb://localhost:27017/")
mydb=client["LIFRANUMdb"]
collection=mydb.myBlogsInfo
Comments=mydb.BlogComments
Posts=mydb.BlogPosts
Pages=mydb.BlogPages
Infos=mydb.BlogInfos
temp=mydb.mytemporarycollection
Sessions=mydb.s
infos=Infos.find()
comments=Comments.find()
pages=Pages.find()
posts=Posts.find()
sessions=Sessions.find()



dash.register_page(__name__, path='/')


layout = html.Div(children=[

           dcc.Location(id='urlhome',refresh=False),
           html.Div(id='mysearchbar',children=[

           dcc.Input(id='mysearchinput',readOnly=False,placeholder='entrez votre recherche ici',type='text',autoComplete='off'),
           html.Br(),
           html.Div(id='myelements',className='dropdown-content',children=[
           html.Ul(id='document-list')]),
   ]),
               

    html.Div(id="searchButtons",className="searchButtons",children=[
     html.Button(id="my-button"),
     dcc.Link(id='search',children="Recherche",href="#"),
    ]),
    html.Div([
    html.Img(id='myimg',src='/assets/logo.png'),

]),
    html.Div([
    html.Img(id='searchpng',src='/assets/search.png')
]),
    html.Button(id="filter",type='submit',children='+',n_clicks=0),
    html.Div(id='filters',children=[
              html.Div(id='title',children=[
                  dcc.Input(id='titleInput',placeholder="Entrez le titre exact",autoComplete='off')
              ]),
              html.Div(id='author',children=[
                  dcc.Input(id='auuthorInput', placeholder="Entrez le nom d'un auteur",autoComplete='off')
              ]),
              html.Div(id='inlinediv',children=[
                     html.Div(id='type',children=[
                         dcc.Dropdown(
                    id='typeInput',
                    options=[
                        {'label': 'Comment', 'value': 'comment'},
                        {'label': 'Post', 'value': 'post'},
                        {'label': 'Page', 'value': 'page'},
                        {'label': 'Blog', 'value': 'blog'}
                    ],
                    placeholder="Entrez le type",
                )
              ]),
              
              ]),
    ]),
    
               dmc.DateRangePicker(id="date",
            placeholder="Date DD/MM/YYYY - DD/MM/YYYY",
            label="2 months",
            style={"width": 330,"backkground-color":"transparent"},
               ),
           
       
    
    html.A("mescollection",id='mescollections', href='/Collections'),
    html.A(id='loginlogout', href='#',style={'background-color':'#007FA2','padding':15,'border-radius':20,'text-decoration':'none',
                                         'color':'white','position':'absolute','top':30,'right':50}),
  
    
    
])
    






