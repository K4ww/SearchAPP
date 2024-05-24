import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, flash, render_template, request, redirect, url_for, session
import string
from pymongo import MongoClient
from dash import Dash, html
from dash import Output,Input,dcc,State,ALL
import nltk
import plotly.graph_objs as go
from urllib.parse import unquote_plus
import dash
import urllib.parse
import uuid  # For generating unique tokens
from flask_mail import Mail, Message
from dash.exceptions import PreventUpdate

nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords
from pymongo import MongoClient

stop_wordsEn=set(stopwords.words('english'))
stop_wordsFr=set(stopwords.words('french'))
client = MongoClient("mongodb://localhost:27017/")
mydb=client["LIFRANUMdb"]
users=mydb.Users
Comments=mydb.BlogComments
Posts=mydb.BlogPosts
Pages=mydb.BlogPages
Infos=mydb.BlogInfos
temp=mydb.mytemporarycollection
collections=mydb.UserCollections

#Flask configuration
Flaskapp = Flask(__name__)
Flaskapp.secret_key = 'your_secret_key'
users_collection = mydb['Users']
# Flask-Mail configuration
Flaskapp.config['MAIL_SERVER'] = 'smtp.gmail.com'
Flaskapp.config['MAIL_PORT'] = 587
Flaskapp.config['MAIL_USE_TLS'] = True
Flaskapp.config['MAIL_USE_SSL'] = False
Flaskapp.config['MAIL_USERNAME'] = 'do.not.replylifranum@gmail.com'
Flaskapp.config['MAIL_PASSWORD'] = 'vqqu vtpy tplp ssep'
Flaskapp.config['MAIL_DEFAULT_SENDER'] = 'do.not.replylifranum@gmail.com'

# Initialize Flask-Mail
mail = Mail(Flaskapp)
# Generate a random secret key
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap','https://fonts.googleapis.com/css2?family=Roboto&display=swap']
external_scripts=['https://code.jquery.com/jquery-3.6.0.min.js']


app = Dash(__name__,server=Flaskapp,external_stylesheets=external_stylesheets, external_scripts=external_scripts,use_pages=True)






app.layout = html.Div([
 dcc.Location(id='urll',refresh=False),
 html.Div(id='dashboard-content',style={'color':'white','position':'absolute','top':50,'left':50}),
 dash.page_container
],style={"padding":"10%","background-color":"#1E1E1E","margin":"auto"})


#callbacks 
@app.callback([Output('filters','style'),Output('date','style'),Output('search','style'),Output('my-button','style'),Output('filter','children'),Output('mysearchinput','style'),Output('title','style'),Output('author','style')],[Input('filter','n_clicks'),Input('typeInput','value')])
def ChosenType(n_clicks,value):
        if not value and n_clicks%2!=0:
          return [{'display':'block'},{'visibility':'visible','width':'330px'},{'display':'block','position':'relative','left':'20%','top':'200%'},{'display':'block','position':'relative','right':'27%','top':'200%'},"-",{'pointer-events': 'none','opacity':'0.5'},{'opacity':'0.5','pointer-events':'none'},{'opacity':'0.5','pointer-events':'none'}]
        elif value=="blog" and n_clicks%2!=0: return [{'display':'block'},{'visibility':'visible','width':'330px'},{'display':'block','position':'relative','left':'20%','top':'200%'},{'display':'block','position':'relative','right':'27%','top':'200%'},"-",{'pointer-events': 'none','opacity':'0.5'},{'opacity':'1'},{'pointer-events': 'none','opacity':'0.5'}]
        elif value=="comment" and n_clicks%2!=0: return [{'display':'block'},{'visibility':'visible','width':'330px'},{'display':'block','position':'relative','left':'20%','top':'200%'},{'display':'block','position':'relative','right':'27%','top':'200%'},"-",{'pointer-events': 'none','opacity':'0.5'},{'pointer-events': 'none','opacity':'0.5'},{'opacity':'1'}]
        elif value=="post" or value=="page" and n_clicks%2!=0: return [{'display':'block'},{'visibility':'visible','width':'330px'},{'display':'block','position':'relative','left':'20%','top':'200%'},{'display':'block','position':'relative','right':'27%','top':'200%'},"-",{'pointer-events': 'none','opacity':'0.5'},{'opacity':'1'},{'opacity':'1'}]

        else: return[{'display':'none'},{'visibility':'hidden','width':'330px'},{},{},"+",{},{},{}]



@app.callback(Output('search', 'href'),
               [Input('typeInput', 'value'),
               Input('auuthorInput', 'value'),
               Input('titleInput', 'value'),
               Input('date','value'),Input('filter','n_clicks'),Input('mysearchinput','value')])
def send_search(search_type, search_author, search_title,search_date,filter,generalesearch):
        if filter%2!=0:
          if search_date is not None:
           url_params = {
        'type': search_type,
        'author': search_author,
        'title': search_title,
        'date':str(search_date[0])+" To "+str(search_date[1]),
        '$':None}
          else:
             url_params = {
        'type': search_type,
        'author': search_author,
        'title': search_title,
        'date':None,
        '$':None}
        

          url_string = '/Result?Filters=' + urllib.parse.urlencode(url_params)
          return url_string
        else:
        
            return f"/Result?={generalesearch}"
            
            




          




@app.callback(Output('InputResult', 'value'),
              [Input('url', 'pathname'), Input('url', 'search')])
def update_output(pathname, search):           
    value = None 
    if "Filters" not in search:
        value = search.split('=')[1]
        value=unquote_plus(value)
        text =" ".join([word for word in value.split() if word not in stop_wordsFr])
        for punctuation in string.punctuation:
             text = text.replace(punctuation, '')
        return text
    else : return None
    

    

def split_string_by_words(text, start_word, end_word):
    words = text.split()  #Split the string into a list of words
    start_index = words.index(start_word)+1  #Find the index of the starting word
    end_index = words.index(end_word)   #Find the index of the ending word (+1 to include it)

    result = ' '.join(words[start_index:end_index])  # Join the words from start to end with a space
    return result


@app.callback([Output("MyResults","children"),Output('NumberOfResults',"children"),Output('NumberOfAuthors','children'),Output('NumberOfLanguages','children'),Output('title','value'),Output('author','value'),Output('type','value'),Output('author-document-bar-graph','figure'),Output('country-document-bar-graph','figure'),Output('Statistics','style')],
              [Input('InputResult', 'value'),Input('url','search')],)
def update_results(value,search):
    MyResults=[]
    
    #if the filter search is used
    if "Filters" in str(search):
       #split the searched filters
       filters=unquote_plus(search.split('Filters')[1])

       filters=filters.replace("="," ")
       filters=filters.replace("&"," ")
       searchedtype=split_string_by_words(str(filters),"type","author")
       searchedauthor=split_string_by_words(str(filters),"author","title")
       searchedtitle=split_string_by_words(str(filters),"title","date")
       if split_string_by_words(str(filters),"date","$")!= "None":
          minsearcheddate=split_string_by_words(str(filters),"date","To").replace('-','/')
          maxsearcheddate=split_string_by_words(str(filters),"To","$").replace('-','/')
          dateformatmin=datetime.datetime.strptime(minsearcheddate,'%Y/%m/%d')
          dateformatmax=datetime.datetime.strptime(maxsearcheddate,'%Y/%m/%d')
          
       else:
           dateformatmin=None
           dateformatmax=None
       #if the searched type is blog then we leave only the title field
       if searchedtype=="blog":
           if split_string_by_words(str(filters),"date","$")!="None" and searchedtitle!="None":
              Infos.aggregate([
             {'$match':{'name':{"$regex":searchedtitle}}},
             {'$match': {'date': {'$gte': dateformatmin, '$lt':dateformatmax }}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
           elif split_string_by_words(str(filters),"date","$")!="None" and searchedtitle=="None":
                Infos.aggregate([
                   
             {'$match': {'date': {'$gte': dateformatmin, '$lt':dateformatmax }}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
           elif split_string_by_words(str(filters),"date","$")=="None" and searchedtitle!="None":
                Infos.aggregate([
             {'$match':{'name':{"$regex":searchedtitle}}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
           resultsScored=temp.find().limit(100)
           for doc in resultsScored[:100]:
               MyResults.append( html.Li(children=[
                    html.Div(id='titleresult',children=[
                              
                  html.A(str(doc['name']), href=doc['url']),
                  html.Img(id='link',src='/assets/link.png'),
                    ]),
                  html.P("type : blog"),
                  html.P(str(doc['description'])[:100]),
                  html.P(str(doc['date']).replace('/','.')[:10],style={'position':'relative','top':'30%','left':'85%'})
              ]))
           NumberOfResults=str(temp.count_documents({}))+" Commentaires"
           temp.delete_many({})
       elif searchedtype=="comment": 
            if split_string_by_words(str(filters),"date","$")!="None" and searchedauthor!="None":
              Comments.aggregate([
             {'$match':{'author.displayName':{"$regex":searchedauthor}}},
             {'$match': {'date': {'$gte': dateformatmin, '$lt':dateformatmax }}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
            elif split_string_by_words(str(filters),"date","$")!="None" and searchedauthor=="None":
                Comments.aggregate([
                   
             {'$match': {'date': {'$gte': dateformatmin, '$lt':dateformatmax }}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
            elif split_string_by_words(str(filters),"date","$")=="None" and searchedauthor!="None":
                Comments.aggregate([
             {'$match':{'author.displayName':{"$regex":searchedauthor}}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
            resultsScored=temp.find().limit(100)
            for doc in resultsScored[:100]:
              if doc['kind']=="blogger#comment":
                if "post" in doc.keys():
                    blogofthiscomment=Posts.find_one({'_id':doc['post']['id']})
                    MyResults.append( 
                  html.Li(children=[
                      html.Div(id='titleresult',children=[
                          
                             html.A(str(doc['content'])[:50]+" ...", href=blogofthiscomment['url']),
                             html.Img(id='link',src='/assets/link.png'),
                      ]),
                  html.P("type : commentaire"),
                  html.P(str(doc['content'])[:100]),
                  html.P(id='keywordBarée'),
                  html.P(str(doc['date']).replace('/','.')[:10],style={'position':'relative','top':'30%','left':'85%'})
                       ]))
                else :
                    MyResults.append( html.Li(children=[
                        html.Div(id='titleresult',children=[
                                      
                  html.A(str(doc['content'])[:50]+" ...", href="#"),
                  html.Img(id='link',src='/assets/link.png'),
                        ]),
                  html.P("type : commentaire"),
                  html.P(str(doc['content'])[:100]),
                  html.P(str(doc['date']).replace('/','.')[:10],style={'position':'relative','top':'30%','left':'85%'})

                       ]))
            NumberOfResults=str(temp.count_documents({}))+" Commentaires"
            temp.delete_many({})
        #if the user searched for posts
       elif searchedtype=="post":
              if split_string_by_words(str(filters),"date","$")!="None" and searchedauthor!="None" and searchedtitle!="None":
                  Posts.aggregate([
             {'$match':{'author.displayName':{"$regex":searchedauthor}}},
             {'$match':{'title':{"$regex":searchedtitle}}},
             {'$match': {'date': {'$gte': dateformatmin, '$lt':dateformatmax }}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])                       
              elif split_string_by_words(str(filters),"date","$")=="None" and searchedauthor!="None" and searchedtitle!="None":
                   Posts.aggregate([
             {'$match':{'author.displayName':{"$regex":searchedauthor}}},
             {'$match':{'title':{"$regex":searchedtitle}}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])  
              elif split_string_by_words(str(filters),"date","$")=="None" and searchedauthor=="None" and searchedtitle!="None":
                  Posts.aggregate([
             {'$match':{'title':{"$regex":searchedtitle}}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
              elif split_string_by_words(str(filters),"date","$")=="None" and searchedauthor!="None" and searchedtitle=="None":
                  Posts.aggregate([
             {'$match':{'author.displayName':{"$regex":searchedauthor}}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])   
              elif split_string_by_words(str(filters),"date","$")!="None" and searchedauthor=="None" and searchedtitle=="None":    
                  Posts.aggregate([
             {'$match': {'date': {'$gte': dateformatmin, '$lt':dateformatmax }}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
              resultsScored=temp.find()
              for doc in resultsScored[:100]:
                  MyResults.append(
                          html.Li(children=[
                      html.Div(id='titleresult',children=[
                          
                  html.A(str(doc['title'])[:50], href=doc['url']),
                  html.Img(id='link',src='/assets/link.png'),
                      ]),
                  html.P("type : post"),
                  html.P(str(doc['content'])[:100]),
                  html.P(str(doc['date']).replace('/','.')[:10],style={'position':'relative','top':'30%','left':'85%'})
              ])
                      )
              NumberOfResults=str(temp.count_documents({}))+" Post(s)"
              temp.delete_many({})
         #if the user searched for pages
       elif searchedtype=="page":
           if split_string_by_words(str(filters),"date","$")!="None" and searchedauthor!="None" and searchedtitle!="None":
                  Pages.aggregate([
             {'$match':{'author.displayName':{"$regex":searchedauthor}}},
             {'$match':{'title':{"$regex":searchedtitle}}},
             {'$match': {'date': {'$gte': dateformatmin, '$lt':dateformatmax }}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])                       
           elif split_string_by_words(str(filters),"date","$")=="None" and searchedauthor!="None" and searchedtitle!="None":
                   Pages.aggregate([
             {'$match':{'author.displayName':{"$regex":searchedauthor}}},
             {'$match':{'title':{"$regex":searchedtitle}}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])  
           elif split_string_by_words(str(filters),"date","$")=="None" and searchedauthor=="None" and searchedtitle!="None":
                  Pages.aggregate([
             {'$match':{'title':{"$regex":searchedtitle}}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
           elif split_string_by_words(str(filters),"date","$")=="None" and searchedauthor!="None" and searchedtitle=="None":
                  Pages.aggregate([
             {'$match':{'author.displayName':{"$regex":searchedauthor}}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])   
           elif split_string_by_words(str(filters),"date","$")!="None" and searchedauthor=="None" and searchedtitle=="None":    
                  Pages.aggregate([
             {'$match': {'date': {'$gte': dateformatmin, '$lt':dateformatmax }}},
             {'$merge': { 'into': "mytemporarycollection" }}
         ]) 
           resultsScored=temp.find()
           for doc in resultsScored[:100]:
                  MyResults.append(
                          html.Li(children=[
                      html.Div(id='titleresult',children=[
                          
                  html.A(str(doc['title'])[:50], href=doc['url']),
                  html.Img(id='link',src='/assets/link.png'),
                      ]),
                  html.P("type : page"),
                  html.P(str(doc['content'])[:100]),
                  html.P(str(doc['date']).replace('/','.')[:10],style={'position':'relative','top':'30%','left':'85%'})
              ])
                      )
           NumberOfResults=str(temp.count_documents({}))+" Page(s)"
           temp.delete_many({})
       
       return [MyResults,NumberOfResults,None,None,searchedtitle,searchedauthor,searchedtype,None,None,{'display':'none'}]
           
    else:
        #if the user made a general search without using the filters
        text =" ".join([word for word in value.split() if word not in stop_wordsFr])
        for punctuation in string.punctuation:
             text = text.replace(punctuation, '')

        

        Comments.aggregate([
             {'$match':{"$text": {"$search": text}}},
             {"$limit": 100},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])
        Posts.aggregate([
             {'$match':{"$text": {"$search": text}}},
             {"$limit": 100},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])
        Infos.aggregate([
             {'$match':{"$text": {"$search": text}}},
             {"$limit": 100},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])
        Pages.aggregate([
             {'$match':{"$text": {"$search": text}}},
             {"$limit": 100},
             {'$merge': { 'into': "mytemporarycollection" }}
         ])
        resultsScored=temp.find({"$text": {"$search": text}}).sort([('score', { '$meta': 'textScore' })]).limit(100)

        for doc in resultsScored:
            blog_id = doc['_id']  # Get the _id of the document
            if doc['kind']=="blogger#comment":
                
                if "post" in doc.keys():
                    blogofthiscomment=Posts.find_one({'_id':doc['post']['id']})
                    existword=" ".join([word for word in text.split(' ') if word in doc['content'] or word in doc['author']['displayName'] ])
                    notexistword=" ".join([word for word in text.split(' ') if word not in doc['content'] and word not in doc['author']['displayName'] ])
                    MyResults.append( 
                  html.Li(children=[
                      html.Div(id='titleresult',children=[
                          
                             html.A(str(doc['content'])[:50]+" ...", href=blogofthiscomment['url']),
                             html.Img(id='link',src='/assets/link.png'),
                      ]),
                  html.Button('Save', id={"type": "save", "index": blog_id},n_clicks=0,style={'position':'relative','left':'2%'}),
                  html.P("type : commentaire"),
                  html.P(str(doc['content'])[:100]),
                  html.P(id='keywordBarée',children=[
                      html.P(children=[
                          html.Del(notexistword),
                      ]), html.P(existword)
                  ])
                       ]))
                    
                    
                          
                else :
                    existword=" ".join([word for word in text.split(' ') if word in doc['content'] or word in doc['author']['displayName'] ])
                    notexistword=" ".join([word for word in text.split(' ') if word not in doc['content'] and word not in doc['author']['displayName'] ])
                    MyResults.append( html.Li(children=[
                        html.Div(id='titleresult',children=[
                                      
                  html.A(str(doc['content'])[:50]+" ...", href="#"),
                  html.Img(id='link',src='/assets/link.png'),
                        ]),
                  html.Button('Save', id={"type": "save", "index": blog_id},n_clicks=0,style={'position':'relative','left':'2%'}),
                  html.P("type : commentaire"),
                  html.P(str(doc['content'])[:100]),
                  html.P(id='keywordBarée',children=[
                      html.P(children=[
                          html.Del(notexistword),
                      ]), html.P(existword)
                  ])
                       ]))
            elif doc['kind']=="blogger#blog":
                existword=" ".join([word for word in text.split(' ') if word in doc['description'] or word in doc['name']])
                notexistword=" ".join([word for word in text.split(' ') if word not in doc['description'] and word not in doc['name']])
                MyResults.append( html.Li(children=[
                    html.Div(id='titleresult',children=[
                              
                  html.A(str(doc['name']), href=doc['url']),
                  html.Img(id='link',src='/assets/link.png'),
                    ]),
                  html.Button('Save', id={"type": "save", "index": blog_id},n_clicks=0,style={'position':'relative','left':'2%'}),
                  html.P("type : blog"),
                  html.P(str(doc['description'])[:100]),
                  html.P(id='keywordBarée',children=[
                      html.P(children=[
                          html.Del(notexistword),
                      ]), html.P(existword)
                  ])
              ]))
                
            elif doc['kind']=="blogger#page":
                MyResults.append( html.Li(children=[
                    html.Div(id='titleresult',children=[
                                 
                  html.A(str(doc['title']), href=doc['url']),
                  html.Img(id='link',src='/assets/link.png'),
                    ]),
                  html.Button('Save', id={"type": "save", "index": blog_id},n_clicks=0,style={'position':'relative','left':'2%'}),
                  html.P("type : page"),
                  html.P(str(doc['content'])[:100])
              ]))
            elif doc['kind']=="blogger#post":
                  if len(str(doc['title']))>50:
                      MyResults.append(
                          html.Li(children=[
                      html.Div(id='titleresult',children=[
                          
                  html.A(str(doc['title'])[:50], href=doc['url']),
                  html.Img(id='link',src='/assets/link.png'),
                      ]),
                  html.Button('Save', id={"type": "save", "index": blog_id},n_clicks=0,style={'position':'relative','left':'2%'}),
                  html.P("type : post"),
                  html.P(str(doc['content'])[:100])
              ])
                      )
                  else:
                     MyResults.append( html.Li(children=[
                      html.Div(id='titleresult',children=[
                          
                  html.A(str(doc['title']), href=doc['url']),
                  html.Img(id='link',src='/assets/link.png'),
                      ]),
                  html.Button('Save', id={"type": "save", "index": blog_id},n_clicks=0,style={'position':'relative','left':'2%'}),
                  html.P("type : post"),
                  html.P(str(doc['content'])[:100])
              ]))
        query={"author": {"$exists": True}}
        distinct_authors = temp.distinct("author.displayName", query)
        NumberOfAuthors=str(len(distinct_authors))+" auteurs"
        query2={"locale": {"$exists": True}}
        distinct_languages = temp.distinct("locale.language", query2)
        NumberOfLanguages=str(len(distinct_languages))+" Langues"
        NumberOfResults=str(Comments.count_documents({"$and":[{"$text": {"$search": text}},{'kind':'blogger#comment'}]}))+" Commentaires et "+str(Posts.count_documents({"$and":[{"$text": {"$search": text}},{'kind':'blogger#post'}]}))+" Posts"
        # Query the database to get the count of documents for each author
        pipeline = [
        {
            "$match": {
                "author": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": "$author.displayName",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        },
        {
            "$limit": 10
        }
    ]
        result = list(temp.aggregate(pipeline))

    # Extract data for the graph
        authors = [entry["_id"] for entry in result]
        document_counts = [entry["count"] for entry in result]

    # Create the graph
        data = [
        {'x': authors, 'y': document_counts, 'type': 'bar', 'name': 'Nombre des documents par auteur'}
    ]
        
        Myanalyse={
        'data': data,
        'layout': go.Layout(
            title='Nombre des documents par auteur',
                    xaxis={'title': 'Auteur'},
                    yaxis={'title': 'Nombre des documents'},
                    
                    plot_bgcolor='#1E1E1E',  # Set background color
                    paper_bgcolor='#1E1E1E',  # Set background color for the entire graph area
                    font={'color': 'white'}  #
        )
    }
        pipeline = [
        {
            "$match": {
                "kind": "blogger#blog",
                "locale.language": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": "$locale.language",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
        result = list(temp.aggregate(pipeline))

    # Extract data for the graph
        contries = [entry["_id"] for entry in result]
        document_counts = [entry["count"] for entry in result]

    # Create the graph
        data = [
        {'x': contries, 'y': document_counts, 'type': 'bar', 'name': 'Nombre des documents par pays'}
    ]
        
        MyanalysePays={
        'data': data,
        'layout': go.Layout(
            title='Nombre des blogs par pays',
                    xaxis={'title': 'Pays'},
                    yaxis={'title': 'Nombre des blogs'},
                    
                    plot_bgcolor='#1E1E1E',  # Set background color
                    paper_bgcolor='#1E1E1E',  # Set background color for the entire graph area
                    font={'color': 'white'}  
        )
    }
        temp.delete_many({})
        return [MyResults,NumberOfResults,NumberOfAuthors,NumberOfLanguages,None,None,None,Myanalyse,MyanalysePays,{}]

from dash import callback_context
import json
from bson import ObjectId
last_clicked_save_id = None
last_clicked_collection_id = None
@app.callback(
     [Output('side-menu', 'style'),Output('side-menu','children')],
    [Input({"type": "save", "index": ALL}, "n_clicks"),Input({"type": "collection", "index": ALL}, "n_clicks")]
)
def update_output(n_clicks,collection):
    menu_content = []
    global last_clicked_save_id
    global last_clicked_collection_id

    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    dic=json.loads(triggered_id)
    if dic["type"]=="save":
        # Save button was clicked
        last_clicked_save_id = dic["index"]
        print("you saved the button:"+last_clicked_save_id)
        if 'user' in session:
         usercollections = collections.find({'iduser': session['user_id']})
         if usercollections.count() != 0:
    #         # If user has a collection, display menu with collection names
    #         # Replace this with your logic to generate menu items based on user's collections
             for collection_item in usercollections:
                 button_id = f"{collection_item['_id']}"
                 button_label = collection_item['name']
                 menu_content.append(html.Button(button_label, id={"type":"collection","index":button_id}, n_clicks=0,style={'position':'relative','margin-top':'20px','margin-left':'10px'}))
             return [{'background-color': 'transparent', 'width': '60%', 'height': '50%', 'position': 'relative', 'display': 'block', 'border': '0.5px solid white'},menu_content]

    elif dic["type"]=="collection":
        # Save button was clicked
        last_clicked_collection_id = dic["index"]
        print(last_clicked_save_id)
        print("in the collection :"+last_clicked_collection_id)
        objectid=ObjectId(str(last_clicked_collection_id))
        collections.update_one({'_id': objectid, 'documents': {'$ne': last_clicked_save_id}}, {'$addToSet': {'documents': last_clicked_save_id}})
        return [{'background-color': 'transparent', 'width': '60%', 'height': '50%', 'position': 'relative', 'display': 'none', 'border': '0.5px solid white'},menu_content]


@app.callback(
    Output('mescollections', 'style'),
    Input('urll', 'pathname')
)
def buttoncollections(pathname):
    if 'user' in session:
        return {'background-color':'#007FA2','padding':15,'border-radius':20,'text-decoration':'none',
                                         'color':'white','position':'absolute','top':30,'right':180,'display':'block'}
    else:
        return {'background-color':'#007FA2','padding':15,'border-radius':20,'text-decoration':'none',
                                         'color':'white','position':'absolute','top':30,'right':180,'display':'none'}
myfile=[]
clicked_collection_id=None
namecollection=None
@app.callback(
     [Output('Mycollections', 'children'),Output("download-text", "data")],
    [Input('urll','pathname'),Input({"type": "supprimer", "index": ALL}, "n_clicks"),Input({"type": "partager", "index": ALL}, "n_clicks"),Input('ajoutercollection','n_clicks'),
     Input('newcollectionname','value')],
    
)      
def show_collection(pathname,supprimer,partager,clickajouter,newcollectioname):
  global clicked_collection_id
  global myfile
  global namecollection
  Mycollections=[]
  ctx = callback_context
  triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
  print(triggered_id)
  if triggered_id!=None and triggered_id!="ajoutercollection":
      dicc=json.loads(triggered_id)
      print(dicc["type"])
      if dicc["type"]=="supprimer":
        # Save button was clicked
        clicked_collection_id = dicc["index"]
        objectid=ObjectId(str(clicked_collection_id))
        collections.delete_one({"_id": objectid})
        print("you wanted to delete the collection:"+clicked_collection_id)
      
      elif dicc["type"]=="partager":
           titres=[]
           clicked_collection_id = dicc["index"]
           objectid=ObjectId(str(clicked_collection_id))
           collectiontofind=collections.find_one({"_id": objectid})
           namecollection=collectiontofind["name"]
           doccollect=collectiontofind['documents']
           collection_names = mydb.list_collection_names()
           for id in doccollect:
              for collection_name in collection_names:
                   collection = mydb[collection_name]
                   document = collection.find_one({"_id": id})
                   if document:
                       titres.append(document['url'])
                       break
           myfile=titres
  if clickajouter!=0 and newcollectioname:
              document = {
    "name": newcollectioname,
    "iduser": session['user_id'],
    "documents": []}
              
              collections.insert_one(document)

           
      
          
  if 'user' in session:
        # Query MongoDB to retrieve all documents
    documents = collections.find({'iduser': session['user_id']})
    for doc in documents:
        titres=[]
        doccollect=doc['documents']
        for id in doccollect:
            # Get list of collection names in the database
            collection_names = mydb.list_collection_names()
            print(id)
            # Iterate over each collection and search for the document by ID
            
            for id in doccollect:
              for collection_name in collection_names:
                   collection = mydb[collection_name]
                   document = collection.find_one({"_id": id})
                   if document:
                       titres.append(document['url'])
                       break
                    
        Mycollections.append(
                          html.Li(children=[
                      html.Div(id='titleresult',children=[
                          dcc.Input(id={"type":"newname","index":str(doc['_id'])},style={'display':'none'}),
                  html.A(str(doc['name'])[:50], href='#'),
                      ]),
                      html.Div(id="buttonscollect",children=[
                      html.Button("supprimer",id={"type":"supprimer","index":str(doc['_id'])},n_clicks=0),
                      html.Button("partager",id={"type":"partager","index":str(doc['_id'])},n_clicks=0),],style={'position':'relative','margin-left':'10px'}),
                      html.Hr(),  # Ajoute une ligne horizontale
                      html.Div(id='documents',children=[html.Ul([html.Li(html.A(doc_item,href=doc_item),style={'position':'relative','margin-bottom':'5px',
                                                                                         'width':'fit-content','height':'fit-content','color':'white','margin-left':'0%'}) for doc_item in titres],id='documents')],style={'position':'relative'
                                                                                ,'margin-top':'10px','padding-left':'0px'})

                       ],style={'overflow': 'scroll'})
                      )
    print(myfile)
    if len(myfile)==0:
        return [Mycollections,None]
    else:
        return [Mycollections,dict(content=str(myfile).strip('[]'), filename=f'{namecollection}'+'.txt')]




#flask functions 
@app.callback(
    [Output('dashboard-content', 'children'),Output('loginlogout','href'),Output('loginlogout','children')],
    [Input('urll', 'pathname')]
)

def display_dashboard(pathname):
    if 'user' in session:
        # Perform searches or display user-specific information here
        return [ f'Hello, {session["name"]}!','/logout','Logout']
    else:
        return [ "",'/login','Login']


@Flaskapp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']  # Get name from form
        family_name = request.form['family_name']  # Get family name from form
        password = request.form['password']
        confirm_password = request.form['confirm_password']  # Get password confirmation from form
        
        # Check if the email domain is allowed
        allowed_domains = ['univ-lyon2.fr', 'univ-lyon1.fr','univ-lyon3.fr']
        if not any(email.endswith(domain) for domain in allowed_domains):
            flash("You don't have the right to use this app with the provided email.")
            return redirect(url_for('register'))
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))
        # Check if user already exists
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('register'))
        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='sha256')

        # Generate a unique verification token
        verification_token = str(uuid.uuid4())

        # Store user information and verification token in the database
        users_collection.insert_one({'email': email, 'password': hashed_password, 'verified': False, 'verification_token': verification_token,'name':name,'familyname':family_name})

        # Send the verification email
        send_verification_email(email, verification_token)

        flash("A verification email has been sent to your email address. Please check your inbox and click the verification link to complete the registration.")
        return redirect(url_for('login'))

    return render_template('register.html')
def send_verification_email(email, token):
    verification_link = url_for('verify_email', token=token, _external=True)
    message = Message('Verify your email', recipients=[email])
    message.body = f'To complete your registration, click the following link: {verification_link}'
    mail.send(message)

@Flaskapp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email, 'verified': True})
        # Check if email exists
        user = users_collection.find_one({'email': email})
        if not user:
            flash('Email does not exist.')
            return redirect(url_for('login'))
        # Check if password is correct
        if not check_password_hash(user['password'], password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
        # Check if user is verified
        if not user.get('verified'):
            flash('Please verify your email before logging in.')
            return redirect(url_for('login'))
        #if informations are right and user is verified log him in
        if user and check_password_hash(user['password'], password):
            # Store user session information
            session['user'] = email
            session['name']=user['name']
            session['user_id']=str(user['_id'])
            return redirect(url_for('/'))

    return render_template('login.html')

@Flaskapp.route('/verify/<token>')
def verify_email(token):
    user = users_collection.find_one({'verification_token': token})

    if user:
        # Mark the user as verified
        users_collection.update_one({'_id': user['_id']}, {'$set': {'verified': True}})
        flash('Your email has been successfully verified. You can now log in.')
    else:
        flash('Invalid verification token. Please try again or register.')

    return redirect(url_for('login'))
@Flaskapp.route('/logout')
def dashboard_logout():
    # Clear user session
    session.pop('user', None)
    return redirect(url_for('login'))
if __name__ == '__main__':
	app.run_server(debug=True,port=5059)