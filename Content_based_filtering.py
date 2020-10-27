import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


def concat(x):
    return ''.join(x['genres'].replace(',',' '))+' '+''.join(x['directors'].replace(',',' '))+' '+''.join(x['writers'].replace(',',' '))

def recomendations(title,howManySuggestions=10):

    data = pickle.load(open("datasets/title.merged.sav", "rb"))
    data['key_data']=data.apply(concat,axis=1)

    count = CountVectorizer()
    count_matrix  =  count . fit_transform ( data[ 'key_data'])

    id=((np.where(data["primaryTitle"] == title))[0])[0]

    cosine_sim = cosine_similarity(count_matrix[id], count_matrix)

    recommended_movies = []

    score_series = pd.Series(cosine_sim[0]).sort_values(ascending=False)

    top_indexes = list(score_series.iloc[0:howManySuggestions+1].index)



    for i in top_indexes:
        recommended_movies.append(list(data['primaryTitle'])[i])

    recommended_movies.remove(title)

    return recommended_movies

