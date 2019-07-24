#%%
from src.transforming import  csvs_to_df, clean_text, create_corpus, tokenize_corpus
from src.scraping import user_totals
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize, punkt

import pandas as pd 
import numpy as np
from collections import Counter
import operator

import holoviews as hv 

hv.extension('bokeh')

#%%
#%%
#combine csvs to a dataframe
data_path = '/Users/keatra/Galvanize/Projects/Instagram_likes_nlp/data_2'
df_raw = csvs_to_df(data_path)
df_raw.head()

#%%
#Plot the number of likes on a histogram
num_likes = hv.Histogram(np.histogram(df_raw['number_of_likes'], 250))
num_likes.opts(xlabel='Number of Likes per photo', xticks=10)
num_likes.redim(x=hv.Dimension('x', range=(0, 200)))


#%%
users= [ 'adizz82', 'blake.kelch', 'briannanmoore13', 'caseybarnold', 'cclay2', 'copperhead_etx', 'faithandfuel',
                'fitness_with_mercy', 'fresco5280', 'happy_hollydays_', 'jhousesrt8','_knesbitt', 'mckensiejoo', 
                'oletheamclachlan', 'phensworld', 'richardrobinsonmusic', 'sirlawrencecharles', 'keilam7', 'dr_kerrie', 
                'pina.risa', 'presmith', 'giftedhands_crochet_and_crafts','jeffersonmason4', 'dmdanamitchell', 
                'suntanned_superman_', 'laceycooley', 'goulding_jr']
user_totals = user_totals(users)
#%%
user_totals['number_of_followers'] = user_totals['number_of_followers'].apply(lambda x: x.replace('.', '') if type(x)==str else x)
user_totals['number_of_followers'] = user_totals['number_of_followers'].apply(lambda x: x.replace('k', '000') if type(x)==str else x)
user_totals['number_of_followers']= user_totals['number_of_followers'].astype(int)
user_totals.describe()

#%%
drop_high_users = user_totals.drop(labels=['jeffersonmason4', 'dmdanamitchell'])
drop_high_users.describe()
#%%
#Plot the number of posts
num_posts = hv.Histogram(np.histogram(user_totals['number_of_posts'], 50))
num_posts.opts(xlabel='Number of Posts per User', xticks=10)
num_posts.redim(x=hv.Dimension('x', range=(0, 800)))
num_posts.redim(y=hv.Dimension('y', range=(0, 4)))


#%%
#Plot the number of followers
num_followers = hv.Histogram(np.histogram(drop_high_users['number_of_followers'], 50))
num_followers.opts(xlabel='Number of Followers per User', xticks=5)
num_followers.redim(x=hv.Dimension('x', range=(0, 1200)))

#%%
#This function will lowercase and remove special characters from the caption 
likes_caption_df  = clean_text(df_raw)
likes_caption_df.head()

#%%
#Create a corpus from the rows in a dataframe
corpus = create_corpus(likes_caption_df)
word_corpus = tokenize_corpus(corpus)
print('There are a total of {} words in the corpus'.format(len(word_corpus)))

#%%
#Create a frequency distribution for word_corpus
words = Counter(word_corpus)
sorted_words = sorted(words.items(), key=operator.itemgetter(1))

#%%
frequency = hv.Scatter(sorted_words[-10:])
frequency.opts(size=7, xlabel='word', ylabel='Number of Times in Corpus')
#%%
#create a train and test set of data
X = np.array(corpus)
y = likes_caption_df['number_of_likes'].values
Xtrain, Xtest, ytrain, ytest = train_test_split(X, y)

#%%
#Create Tf-idf vectorizer and save feature names, vocabulary set, and ignored words
vector_train = TfidfVectorizer(min_df= 0.00017)
X_vector = vector_train.fit_transform(Xtrain)
X_train = X_vector.todense()

popular_words = vector_train.get_feature_names()

vocab = vector_train.vocabulary_
ignored_words = vector_train.stop_words_

#%%
#Create Xtest vector from Xtrain vocabulary
vector_test = TfidfVectorizer(vocabulary=vocab)
X_vect = vector_test.fit_transform(Xtest)
X_test = X_vect.todense().astype(int)

#%%
#Random Forest Regression Model
rf = RandomForestRegressor(n_estimators = 10, max_features=0.33, n_jobs=-1)
rf.fit(X_train, ytrain)
print("Random Forest score:", rf.score(X_test, ytest))

#%%
