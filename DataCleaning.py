import pandas as pd
import random

df_movies=pd.read_csv('IMDB movies.csv')

# User Data Generation

df_users=df_movies[df_movies['actors'].apply(lambda x: ',' not in str(x))]
df_users=df_users[df_users['actors'].notna()]
df_users['email']=df_users.actors.str.replace(' ', '').str.lower()
listmail=['outlook.com','gmail.com','yahoo.com','reddit.com','hotmail.com']
df_users['user_id']=df_users['email'].astype('str')+df_users['year'].astype('str')
df_users['email']=df_users['email'].astype('str')+df_users['year'].astype('str')
df_users['email']=df_users['email'].apply(lambda x:str(x)+'@'+random.choice(listmail))
df_users['country_id']=df_users['email'].apply(lambda x:random.randint(0,110))
df_users['DOB']=df_users['date_published']                                            
df_users['passcode']=df_users['email'].apply(lambda x:random.randint(11000000,99999999))
df_users=df_users[['user_id','email','passcode','country_id','DOB']]
df_users=df_users[df_users['DOB'].apply(lambda x: '-' in str(x))]
df_users=df_users.rename(columns={'user_id':'UserID','email':'UserName','passcode':'Passcode','country_id':'CountryID','DOB':'UserDOB'})
df_users['UserID']=df_users['UserID'].str.replace("'",'')
df_users['UserName']=df_users['UserID'].str.replace("'",'')
df_users=df_users.groupby('UserID',as_index=False).first()
df_users_erd=df_users
df_users_erd.to_csv('Users.csv',index=False)

df_names=pd.read_csv('IMDB names.csv')

df_rating=pd.read_csv('IMDB ratings.csv')

df_title_principles=pd.read_csv('IMDb title_principals.csv')
df_movies_erd=df_movies[['imdb_title_id','duration','title','date_published','country','language','director','genre','description']]
df_movies_erd=df_movies_erd[df_movies_erd['date_published'].apply(lambda x: '-' in str(x))]
df_movies_erd=df_movies_erd.dropna()
df_movies_erd=df_movies_erd[df_movies_erd['genre'].apply(lambda x:',' not in x)]
df_movies_erd=df_movies_erd[df_movies_erd['country'].apply(lambda x:',' not in str(x))]
df_movies_erd=df_movies_erd[df_movies_erd['language'].apply(lambda x: ',' not in str(x))]

# Director
df_name_title_director=df_title_principles[df_title_principles['category']=='director']
df_director_erd=pd.merge(df_name_title_director,df_movies_erd,on='imdb_title_id',how='right')
df_director_erd=df_director_erd[['imdb_title_id','imdb_name_id','director']]
df_director_erd[['first_name','last_name']] = df_director_erd['director'].loc[df_director_erd['director'].str.split().str.len() == 2].str.split(expand=True)
df_director_erd=df_director_erd[df_director_erd['first_name'].notna()]
df_director_erd=df_director_erd[df_director_erd['last_name'].notna()]
df_director_erd=df_director_erd.drop(columns=['director'])
df_names=df_names[['imdb_name_id', 'name','date_of_birth','date_of_death']]
df_title_principles=df_title_principles[['imdb_title_id', 'imdb_name_id','category','characters']]
df_name_title=pd.merge(df_title_principles,df_names,on='imdb_name_id')
# Actor

df_name_title=df_name_title[(df_name_title['category']=='actor') | (df_name_title['category']=='actress') | (df_name_title['category']=='director')]
df_name_title_director=df_name_title[df_name_title['category']=='director']
df_name_title_actor=df_name_title[df_name_title['category']!='director']
df_name_title_actor[['first_name','last_name']] = df_name_title_actor['name'].loc[df_name_title_actor['name'].str.split().str.len() == 2].str.split(expand=True)
df_actors_erd=df_name_title_actor[['imdb_name_id','first_name','last_name']]
df_actors_erd=df_actors_erd.drop_duplicates().reset_index().drop(columns=['index'])

# Cast

df_name_title_actor['characters']=df_name_title_actor['characters'].astype(str)
df_name_title_actor['characters']=df_name_title_actor['characters'].apply(lambda x:x[2:-2])
df_name_title_actor=df_name_title_actor[df_name_title_actor['characters'].apply(lambda x:',' not in x)].reset_index().drop(columns=['index'])
df_cast_erd=df_name_title_actor[['imdb_name_id','imdb_title_id','characters']]

# Genre and Genre_Movie

from sklearn import preprocessing
label_encoder = preprocessing.LabelEncoder()
df_movies_erd['genre_id']= label_encoder.fit_transform(df_movies_erd['genre'])
df_genre_movie_erd=df_movies_erd[['genre_id','imdb_title_id']].reset_index().drop(columns=['index'])
df_genres_erd=df_movies_erd[['genre_id','genre']].drop_duplicates().sort_values(by='genre_id').reset_index().drop(columns=['index'])
df_genre_movie_erd=pd.merge(df_genre_movie_erd,df_genres_erd,on='genre_id',how='inner')
df_genres_erd

df_movies_erd=df_movies_erd.drop(columns=['genre','genre_id'])
df_movies_erd=pd.merge(df_movies_erd,df_director_erd,on='imdb_title_id',how='left')
df_movies_erd=df_movies_erd.drop(columns=['first_name','last_name'])

# Countries

df_movies_erd['country']=df_movies_erd['country'].astype('str')
df_movies_erd['country_id']= label_encoder.fit_transform(df_movies_erd['country'])
df_countries_erd=df_movies_erd[['country','country_id']].drop_duplicates().sort_values(by='country_id').reset_index().drop(columns=['index'])
df_movies_erd=df_movies_erd.drop(columns=['country'])
df_countries_erd

# Generating CSVs


df_movies_erd=df_movies_erd.rename(columns={'imdb_title_id':'MovieID','duration':'Runtime',
                                            'title':'MovieName','date_published':'releaseDate',
                                            'country_id':'CountryID','language':'Language','imdb_name_id':'DirectorID'
                                            ,'description':'Movie_Desc'})
df_movies_erd=df_movies_erd[['MovieID', 'Runtime', 'MovieName', 'releaseDate','CountryID', 'Language',
        'DirectorID', 'Movie_Desc']]

#df_movies_erd.to_csv('Movies.csv',index=False)

df_countries_erd=df_countries_erd.rename(columns={'country_id':'CountryID','country':'CountryName'})
df_countries_erd=df_countries_erd[['CountryID','CountryName']]
df_countries_erd.to_csv('Countries.csv',index=False)

df_genres_erd=df_genres_erd.rename(columns={'genre_id':'GenreID','genre':'Name'})
df_genres_erd.to_csv('Genres.csv',index=False)
# Random sampling and check refrential integrity
df_movies_erd=df_movies_erd.sample(n=1000, random_state=1)
df_movies_erd=df_movies_erd[df_movies_erd['DirectorID'].notna()]
df_actors_erd=df_actors_erd.drop_duplicates().reset_index().drop(columns=['index'])
df_actors_erd=df_actors_erd.rename(columns={'imdb_name_id':'ActorID','first_name':'ActorFirst','last_name':'ActorLast'})
df_actors_erd


df_cast_erd=df_cast_erd.rename(columns={'imdb_name_id':'ActorID','imdb_title_id':'MovieID',
                                        'characters':'ActorScreenName'})

df_cast_erd=df_cast_erd[df_cast_erd['MovieID'].isin(df_movies_erd['MovieID'])].reset_index().drop(columns=['index'])
df_cast_erd['ActorScreenName']=df_cast_erd.ActorScreenName.str.replace('\\', '').str.lower()
df_cast_erd['ActorScreenName']=df_cast_erd.ActorScreenName.str.replace('"', '').str.lower()
df_cast_erd=df_cast_erd.drop_duplicates()
df_cast_erd.to_csv('Cast.csv',index=False)

import numpy as np
import random
df_actors_erd=df_actors_erd[df_actors_erd['ActorID'].isin(df_cast_erd['ActorID'])].reset_index().drop(columns=['index'])
rng = np.random.default_rng()
df_actors_erd['Age']=pd.DataFrame(rng.integers(18, 70, size=(len(df_actors_erd),1)))
df_actors_erd.to_csv('Actors.csv',index=False)

df_director_erd=df_director_erd.rename(columns={'imdb_name_id':'DirectorID','first_name':'firstName',
                                                'last_name':'lastName'})
df_director_erd=df_director_erd.drop(columns=['imdb_title_id'])

import csv
df_movies_erd.to_csv('Movies.csv',index=False,quotechar='"',quoting=csv.QUOTE_ALL)
df_director_erd=df_director_erd[df_director_erd['DirectorID'].isin(df_movies_erd['DirectorID'])]
df_director_erd=df_director_erd[df_director_erd['DirectorID'].notna()].drop_duplicates().reset_index().drop(columns=['index'])
for l in list(df_movies_erd['DirectorID']):
    if l not in list(df_director_erd['DirectorID']):
        print(l)
df_director_erd['isActor']=df_director_erd['DirectorID'].apply(lambda x: x in list(df_actors_erd['ActorID']))
df_director_erd['ActorID']=df_director_erd[df_director_erd['isActor']==True].DirectorID
df_director_erd=df_director_erd.drop(columns=['isActor'])
df_director_erd.to_csv('Director.csv',index=False)
df_genre_movie_erd=df_genre_movie_erd.rename(columns={'imdb_title_id':'MovieID','genre_id':'GenreID','genre':'GenreName'})
df_genre_movie_erd=df_genre_movie_erd[df_genre_movie_erd['MovieID'].isin(df_movies_erd['MovieID'])].reset_index().drop(columns=['index'])
df_genre_movie_erd
df_genre_movie_erd.to_csv('Genre_Movie.csv',index=False)

filewriter=open('Genres.csv')
print('INSERT INTO Genres VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"({l.split(',')[0]},'{l.split(',')[1].strip()}'),")
filewriter.close()

filewriter=open('Countries.csv')
print('INSERT INTO Countries VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"({l.split(',')[0]},'{l.split(',')[1].strip()}'),")
filewriter.close()

filewriter=open('Actors.csv')
print('INSERT INTO Actors VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"('{l.split(',')[0]}',\"{l.split(',')[1]}\",\"{l.split(',')[2]}\",{l.split(',')[3].strip()}),")
filewriter.close()

filewriter=open('Director.csv')
print('INSERT INTO Director VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"('{l.split(',')[0]}',\"{l.split(',')[1]}\",\"{l.split(',')[2]}\",'{l.split(',')[3].strip()}'),")
filewriter.close()



filewriter=open('Movies.csv')
print('INSERT INTO Movies VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"""('{l.split('"')[1]}',{l.split('"')[3]},\"\"\"{l.split('"')[5]}\"\"\",str_to_date('{l.split('"')[7]}','%Y-%m-%d'),{l.split('"')[9]},'{l.split('"')[11]}','{l.split('"')[13]}',\"\"\"{l.split('"')[15].strip()}\"\"\"),""")
filewriter.close()

filewriter=open('Genre_Movie.csv')
print('INSERT INTO GenreMovie VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"('{l.split(',')[1]}',{l.split(',')[0]},'{l.split(',')[2].strip()}'),")
filewriter.close()

filewriter=open('Cast.csv')
print('INSERT INTO Cast VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"""('{l.split(',')[0]}','{l.split(',')[1]}',\"\"\"{l.split(',')[2].strip()}\"\"\"),""")
filewriter.close()

# Reviews
df_reviews=pd.read_csv('IMDB Dataset.csv')
df_reviews['review']=df_reviews['review'].str.replace("<br />",'')
df_reviews['review']=df_reviews['review'].str.replace("\"",'')
df_reviews['ReviewID']=df_reviews.index
df_reviews['UserID']=df_reviews['ReviewID'].apply(lambda x:random.choice(list(df_users['UserID'])))
df_reviews['MovieID']=df_reviews['ReviewID'].apply(lambda x:random.choice(list(df_movies_erd['MovieID'])))
df_reviews['Rating']=df_reviews['ReviewID'].apply(lambda x:random.randint(1,5))
df_reviews=df_reviews.rename(columns={'review':'Review'})
df_reviews_erd=df_reviews[['ReviewID','UserID','Rating','Review','MovieID']][1:2000]
df_reviews_erd.to_csv('Reviews.csv',index=False,quotechar='"',quoting=csv.QUOTE_ALL)
filewriter=open('Users.csv')
print('INSERT INTO Users VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"""('{l.split(',')[0]}','{l.split(',')[1]}','{l.split(',')[2]}',{l.split(',')[3]},str_to_date('{l.split(',')[4].strip()}','%Y-%m-%d')),""")
filewriter.close()
filewriter=open('Reviews.csv')
print('INSERT INTO Reviews VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"""({l.split('"')[1]},'{l.split('"')[3]}',{l.split('"')[5]},\"\"\"{l.split('"')[7][:100]}\"\"\",'{l.split('"')[9].strip()}'),""")
filewriter.close()
df_users['key']=1
df_movies_erd['key']=1
df_movies_users=pd.merge(df_users,df_movies_erd,on='key').drop("key", 1)
import random
sampleList = [1,2,3,4,5]
randomList = random.choices(
  sampleList, weights=(50,40,20,10,5), k=len(df_movies_users))
df_movies_users['NumberOfView']=randomList
df_movies_users=df_movies_users[['MovieID','UserID','NumberOfView']]
df2=pd.DataFrame()
for l in df_movies_users['UserID'].unique():
    list_random_number=random.choices(list(range(1,300)),weights=list(reversed(range(1,300))),k=1)
    df1=df_movies_users[df_movies_users['UserID']==l]
    a=int("".join(map(str, list_random_number)))
    df1=df1.sample(n=a, random_state=10)
    df2=df2.append(df1)
df_movies_users_erd=df2.reset_index().drop(columns=['index'])
df_movies_users_erd.to_csv('df_movies_users.csv',index=False)
filewriter=open('df_movies_users.csv')
print('INSERT INTO Movies_Users VALUES')
lines = filewriter.readlines()[1:]
for l in lines:
    print(f"""('{l.split(',')[0]}','{l.split(',')[1]}',{l.split(',')[2].strip()}),""")
filewriter.close()
