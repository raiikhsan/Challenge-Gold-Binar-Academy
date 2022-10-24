from flask import Flask, jsonify, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import pandas as pd
import sqlite3

app = Flask(__name__)

###############################################################################################################
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda:'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda:'1.0.0'),
        'description': LazyString(lambda:'Dokumentasi API untuk Data Processing dan Modeling')
        }, host = LazyString(lambda: request.host)
    )
swagger_config = {
        "headers":[],
        "specs":[
            {
            "endpoint":'docs',
            "route":'/docs.json'
            }
        ],
        "static_url_path":"/flasgger_static",
        "swagger_ui":True,
        "specs_route":"/docs/"
    }
swagger = Swagger(app, template=swagger_template, config=swagger_config)

###############################################################################################################
conn = sqlite3.connect('challengegoldbinar.db')
cur = conn.cursor()

tweet = pd.read_sql_query("select * from data", conn)
abusive = pd.read_sql_query("select * from abusive", conn)
alay = pd.read_sql_query("select * from new_kamusalay", conn)
twit = tweet['Tweet'].to_list() #ubah kolom tweet jadi list
abusif = abusive['abusive_words'].to_list() #ubah kolom abusive jadi list
alaymentah = alay["alay"].to_list() #ubah kolom alay dan fix_alay jadi list
alayfix = alay["fix_alay"].to_list()
df_get = twit.copy()


def abuse(twit):
    df_get = twit.copy()
    df_get['new'] = df_get['Tweet'].str.lower().to_list()
    list_get = df_get['new'].to_list()
    for i in list_get:
        for j in abusif:
            if j in i:
                k = list_get[list_get.index(i)].replace(j,'****')
                list_get[list_get.index(i)] = k
                i = k
    df_get['new'] = list_get
    json = df_get.to_dict(orient='index')
    del df_get
    return json
#     return df_get['new']

# def slang(df_get):
#     list_get = df_get['new'].to_list()
#     for i in list_get:
#         for j in alaymentah:
#             if j in i:
#                 a = alaymentah.index(j)
#                 k = list_get[list_get.index(i)].replace(j,alayfix[a])
#                 list_get[list_get.index(i)] = k
#                 i = k
#     df_get['new'] = list_get
#     json = df_get.to_dict(orient='index')
#     del df_get
#     return json

# def frame(twit):
#     twit = slang(twit)
#     twit = abuse(twit)
###############################################################################################################

# GET
@swag_from("docsyml/tweet_index.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def test():
	return jsonify({'message' : 'Welcome to Tweet Cleansing API'})

@swag_from("docsyml/tweet_index.yml", methods=['GET'])
@app.route('/tweet', methods=['GET'])
def returnAll():

    json = abuse(tweet)

    return jsonify(json)

###############################################################################################################
# GET
@swag_from("docsyml/tweet_get.yml", methods=['GET'])
@app.route('/tweet/<id>', methods=['GET'])
def returnOne(id):
    
    json = abuse(tweet)
    
    id = int(id)
    json = json[id]

    return jsonify(json)

###############################################################################################################
#POST
@swag_from("docsyml/tweet_post.yml", methods=['POST'])
@app.route('/tweet', methods=['POST'])
def addOne():
        global tweet
        new_tweet = {'Tweet': request.json['Tweet']}
        pd_new_tweet = pd.DataFrame.from_dict([new_tweet])
        tweet = pd.concat([tweet, pd_new_tweet], ignore_index=True)
        print(tweet.tail(2))
        return 'berhasil'

###############################################################################################################

@swag_from("docsyml/tweet_csv.yml", methods=['POST'])
@app.route('/tweet/upload', methods=['POST'])
def upload_csv():
    global tweet
    if request.method == 'POST':
        file = request.files['file']
        try:
            data = pd.read_csv(file, encoding='iso-8859-1')
        except:
            data = pd.read_csv(file, encoding='utf-8') 
        print(0)
        print(tweet.tail(1))
        tweet = pd.concat([tweet, data], ignore_index=True)
        print(data.head())
        print(1)
        print(tweet.tail(2))
        return "DONE"

# Cari code flask untuk upload file
# file nya di baca oleh pandas
# pandas ekstrak data
# upload ke DB

#     return jsonify(json)

###############################################################################################################
if __name__ == "__main__":
    app.run()