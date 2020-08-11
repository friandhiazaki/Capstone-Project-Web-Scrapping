from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__) #don't change this code

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    main_webpage = soup.find('div', attrs={'class':'article'}) 
    box_movie = soup.find_all('div', attrs={'class':'lister-item-content'}) 

    temp = [] #initiating a tuple

    for i in range(0, len(box_movie)):
        box_webpage = main_webpage.find_all('div', attrs={'class':'lister-item-content'})[i]

        #Get Title
        judul = box_webpage.find_all('a')[0].text

        #Get Rating
        imdb_rating = box_webpage.find_all('strong')[0].text

        #Get Metascore
        metascore = box_webpage.find('span', attrs={'class':'metascore favorable'})
        if metascore is not None:
            metascore = metascore.text.strip()
        else:
            metascore = None
        
        #Get Movie Votes
        votes = box_webpage.find_all('span', attrs={'name':'nv'})[0].text

        #use the key to take information here
        #name_of_object = row.find_all(...)[0].text






        temp.append((judul,imdb_rating,metascore,votes)) #append the needed information 
    
    temp

    dataset_movie = pd.DataFrame(temp, columns = ('Judul','Imdb_Rating','Metascore','Votes')) #creating the dataframe
   #data wranggling -  try to change the data type to right data type
    dataset_movie['Votes'] = dataset_movie['Votes'].apply(lambda x: x.replace(',','.'))
    dataset_movie['Metascore'] = pd.to_numeric(dataset_movie['Metascore'], errors='coerce')
    dataset_movie[['Imdb_Rating','Votes']] = dataset_movie[['Imdb_Rating','Votes']].astype('float64')
   
   #end of data wranggling

    return dataset_movie

@app.route("/")
def index():
    dataset_movie = scrap('https://imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    top_7movies = dataset_movie.sort_values(by=['Votes'], ascending=False).head(7)
    top_7movies = top_7movies.set_index('Judul')
    ax = top_7movies['Votes'].sort_values(ascending=True).plot(kind='barh', title='Top 7 Movies')
    ax.set_xlabel('Votes')
    ax.set_ylabel('Judul')
    plt.tight_layout()

    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    dataset_movie = dataset_movie.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=dataset_movie, result=result)


if __name__ == "__main__": 
    app.run()
