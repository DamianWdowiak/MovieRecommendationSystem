import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from resources import titles_data, users_data, count_matrix


def content_filter(userId, n_recommendations=10):
    movies_watched_by_user = users_data[users_data.userId == userId].sort_values(by='rating', ascending=False).tconst
    top_rated_by_user = movies_watched_by_user[:10]

    recommended_movies = set()
    for tconst in top_rated_by_user:
        id = ((np.where(titles_data.tconst == tconst))[0])[0]

        cosine_sim = cosine_similarity(count_matrix[id], count_matrix)

        score_series = pd.Series(cosine_sim[0]).sort_values(ascending=False)

        top_indexes = list(score_series.iloc[0:n_recommendations + 1].index)

        for i in top_indexes:
            movie = titles_data['tconst'].values[i]
            if movie not in list(movies_watched_by_user):
                recommended_movies.add(movie)

    return list(recommended_movies)[: n_recommendations]
